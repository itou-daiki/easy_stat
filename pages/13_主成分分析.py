import io
import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from PIL import Image
import common

common.set_font()

# ページ設定
st.set_page_config(page_title="主成分分析", layout="wide")
st.title("主成分分析")
common.display_header()
st.write("")
st.subheader("ブラウザで検定 → 表 → 解釈まで出力できるウェブアプリです。")
st.write("iPad等でも分析を行うことができます")
st.write("")

# --- ファイルアップロード・デモデータの読み込み ---
uploaded_file = st.file_uploader("ExcelまたはCSVファイルをアップロードしてください", type=["xlsx", "csv"])
use_demo_data = st.checkbox("デモデータを使用")

@st.cache_data
def load_data(file):
    """
    アップロードされたファイルを読み込み、DataFrameとして返す関数
    ExcelまたはCSV形式に対応
    """
    try:
        if file.type == "text/csv":
            return pd.read_csv(file)
        elif file.type in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
        ]:
            return pd.read_excel(file)
        else:
            st.error("対応していないファイル形式です。")
            return None
    except Exception as e:
        st.error(f"データの読み込み中にエラーが発生しました: {e}")
        return None

df = None
if use_demo_data:
    try:
        # ※ デモデータのファイルパスは適宜変更してください
        df = pd.read_excel("datasets/factor_analysis_demo.xlsx", sheet_name=0)
    except Exception as e:
        st.error(f"デモデータの読み込みに失敗しました: {e}")
elif uploaded_file is not None:
    df = load_data(uploaded_file)

if df is not None:
    st.write("【入力データ】")
    st.dataframe(df.head())

    # --- 数値変数の抽出 ---
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    if len(numerical_cols) == 0:
        st.error("データ内に数値変数が見つかりません。")
    else:
        # --- 主成分分析用の変数選択（デフォルトで全数値変数を選択） ---
        st.subheader("主成分分析の設定")
        selected_vars = st.multiselect('分析対象の変数を選択してください', numerical_cols, default=numerical_cols)
        if len(selected_vars) == 0:
            st.error("少なくとも1つの数値変数を選択してください。")
        else:
            # 選択された変数のみを使用
            df_selected = df[selected_vars]
            st.write("【分析に使用するデータ】")
            st.dataframe(df_selected.head())

            # --- PCAの実行 ---
            scaler = StandardScaler()
            df_scaled = scaler.fit_transform(df_selected)
            
            # 主成分の数は選択可能（上限は選択変数数と8のうち小さい方）
            n_components = st.slider("主成分の数を選択してください", 1, min(len(selected_vars), 8))
            pca = PCA(n_components=n_components)
            components = pca.fit_transform(df_scaled)
            
            # --- 説明分散比率の表示 ---
            explained_df = pd.DataFrame({
                "主成分": [f"PC{i+1}" for i in range(n_components)],
                "説明分散比率": pca.explained_variance_ratio_
            })
            st.subheader("【各主成分の説明分散比率】")
            st.dataframe(explained_df.style.format({"説明分散比率": "{:.3f}"}))
            
            # --- 主成分得点の表示 ---
            pc_df = pd.DataFrame(components, columns=[f"PC{i+1}" for i in range(n_components)])
            st.subheader("【各サンプルの主成分得点】")
            st.dataframe(pc_df.style.format("{:.3f}"))
            
            # --- 主成分のロードings（係数）の表示 ---
            loading_df = pd.DataFrame(pca.components_.T,
                                      index=selected_vars,
                                      columns=[f"PC{i+1}" for i in range(n_components)])
            st.write("【各主成分のロードings（係数）】")
            st.dataframe(loading_df.style.format("{:.3f}"))
            
            # === 追加機能：縮約された（＝主成分に強く寄与している）項目の表示 ===
            st.subheader("主成分への寄与が大きい元の変数の表示")
            # 寄与度の閾値をユーザーが設定（絶対値）
            threshold = st.slider("寄与度の閾値を設定してください（絶対値）", 0.0, 1.0, 0.5, step=0.05)
            pc_contributions = {}
            for pc in loading_df.columns:
                # 各主成分で絶対値が閾値以上の変数を抽出
                significant_vars = loading_df[pc].abs() >= threshold
                variables = loading_df.index[significant_vars].tolist()
                pc_contributions[pc] = ", ".join(variables) if variables else "なし"
            st.write(pd.DataFrame(list(pc_contributions.items()), columns=["主成分", "寄与が大きい変数"]))
            
            # === 追加機能：バイプロットの表示（主成分が2つ以上の場合） ===
            if n_components >= 2:
                st.subheader("バイプロット (PC1 vs PC2)")
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(figsize=(8,6))
                # 主成分得点の散布図
                ax.scatter(components[:,0], components[:,1], alpha=0.5)
                # 各変数のベクトル（ロードings）を表示
                for var in selected_vars:
                    x = loading_df.loc[var, "PC1"]
                    y = loading_df.loc[var, "PC2"]
                    # スケール調整のため、主成分得点の最大値を取得
                    scale_x = max(abs(components[:,0]))
                    scale_y = max(abs(components[:,1]))
                    # 矢印でベクトルを描画
                    ax.arrow(0, 0, x*scale_x, y*scale_y, color='red', head_width=0.05, head_length=0.05)
                    ax.text(x*scale_x*1.1, y*scale_y*1.1, var, color='red')
                ax.set_xlabel("PC1")
                ax.set_ylabel("PC2")
                ax.set_title("バイプロット")
                st.pyplot(fig)
            
            # --- Excelファイルへのダウンロード ---
            def convert_df_to_excel(df):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False)
                return output.getvalue()
            
            st.download_button(
                label="主成分得点のみのExcelファイルをダウンロード",
                data=convert_df_to_excel(pc_df),
                file_name="pca_scores.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# --- フッター表示 ---
common.display_copyright()
common.display_special_thanks()
