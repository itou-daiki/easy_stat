import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
import matplotlib.pyplot as plt
import japanize_matplotlib
from PIL import Image
import io
from scipy.stats import chi2
import common

# ページ設定
st.set_page_config(page_title="因子分析", layout="wide")
st.title("因子分析")
common.display_header()
st.write("データから因子構造を抽出し、因子負荷量、適合度指標、信頼性係数、そして因子平均を算出・ダウンロードできます。")

# --- データ読み込み処理の関数化 ---
@st.cache_data
def load_data(file):
    """
    アップロードされたファイルを読み込み、DataFrameを返す
    """
    try:
        if file.type == 'text/csv':
            return pd.read_csv(file)
        elif file.type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
            return pd.read_excel(file)
        else:
            st.error("対応していないファイル形式です。")
            return None
    except Exception as e:
        st.error(f"データの読み込み中にエラーが発生しました: {str(e)}")
        return None

# --- データのアップロードまたはデモデータの利用 ---
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])
use_demo_data = st.checkbox('デモデータを使用')

df = None
if use_demo_data:
    try:
        df = pd.read_excel('datasets/factor_analysis_demo.xlsx', sheet_name=0)
    except Exception as e:
        st.error(f"デモデータの読み込みに失敗しました: {str(e)}")
else:
    if uploaded_file is not None:
        df = load_data(uploaded_file)

if df is not None:
    # --- データプレビュー（折りたたみ表示） ---
    with st.expander("データプレビュー"):
        st.dataframe(df.head())

    # --- 数値変数の抽出 ---
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    if len(numerical_cols) == 0:
        st.error("データ内に数値変数が見つかりません。")
    else:
        # --- 因子分析用の変数選択（デフォルトで全数値変数を選択） ---
        st.subheader("因子分析の設定")
        selected_vars = st.multiselect('分析対象の変数を選択してください', numerical_cols, default=numerical_cols)
        
        if len(selected_vars) < 3:
            st.warning('少なくとも3つの変数を選択してください。')
        else:
            # --- 分析手法と回転方法の選択 ---
            col1, col2 = st.columns(2)
            with col1:
                method = st.selectbox(
                    '因子抽出法を選択してください',
                    ['最尤法', '主成分法', '主軸法'],
                    format_func=lambda x: {
                        '最尤法': '最尤法 (Maximum Likelihood)',
                        '主成分法': '主成分法 (Principal Component)',
                        '主軸法': '主軸法 (Principal Axis)'
                    }[x]
                )
            
            with col2:
                rotation = st.selectbox(
                    '回転方法を選択してください',
                    ['プロマックス回転', 'バリマックス回転'],
                    format_func=lambda x: {
                        'プロマックス回転': 'プロマックス回転 (Promax)',
                        'バリマックス回転': 'バリマックス回転 (Varimax)'
                    }[x]
                )

            # --- 抽出する因子数の設定 ---
            n_factors = st.slider('抽出する因子数を選択してください', min_value=1, 
                                max_value=len(selected_vars)-1, value=3)

            # --- 分析手法・回転方法の内部表現への変換 ---
            method_dict = {
                '最尤法': 'ml',
                '主成分法': 'principal',
                '主軸法': 'pa'
            }
            rotation_dict = {
                'プロマックス回転': 'promax',
                'バリマックス回転': 'varimax'
            }
            
            # --- KMOとBartlettの球面性検定 ---
            try:
                kmo_all, kmo_model = calculate_kmo(df[selected_vars])
                chi_square_value, p_value = calculate_bartlett_sphericity(df[selected_vars])
                st.write("KMO値:", round(kmo_model, 3))
                st.write("Bartlettの球面性検定:")
                st.write(f"カイ二乗値: {round(chi_square_value, 3)}, p値: {round(p_value, 3)}")
            except Exception as e:
                st.error(f"KMOまたはBartlett検定の計算中にエラーが発生しました: {str(e)}")

            # --- 因子分析の実行 ---
            try:
                fa = FactorAnalyzer(
                    rotation=rotation_dict[rotation],
                    n_factors=n_factors,
                    method=method_dict[method]
                )
                fa.fit(df[selected_vars])
            except Exception as e:
                st.error(f"因子分析の実行中にエラーが発生しました: {str(e)}")
            else:
                # --- スクリープロットの作成 ---
                st.subheader("スクリープロット")
                try:
                    ev, v = fa.get_eigenvalues()
                    fig_scree = go.Figure()
                    fig_scree.add_trace(go.Scatter(x=list(range(1, len(ev)+1)), y=ev,
                                                 mode='lines+markers',
                                                 name='固有値'))
                    fig_scree.add_hline(y=1, line_dash="dash", line_color="red")
                    fig_scree.update_layout(title="スクリープロット",
                                          xaxis_title="因子番号",
                                          yaxis_title="固有値")
                    st.plotly_chart(fig_scree)
                except Exception as e:
                    st.error(f"スクリープロットの作成中にエラーが発生しました: {str(e)}")

                # --- 因子負荷量の計算と表示 ---
                st.subheader("因子負荷量")
                try:
                    loadings = pd.DataFrame(
                        fa.loadings_,
                        columns=[f'Factor{i+1}' for i in range(n_factors)],
                        index=selected_vars
                    )
                    # 共通性の計算
                    communalities = fa.get_communalities()
                    loadings['共通性'] = communalities

                    # 各項目の最大負荷量を持つ因子とその値を特定（各項目は最も寄与する因子に割り当て）
                    factor_assignments = {f'Factor{i+1}': [] for i in range(n_factors)}
                    for idx in loadings.index:
                        factor_loadings = loadings.loc[idx, [f'Factor{i+1}' for i in range(n_factors)]]
                        max_factor = factor_loadings.abs().idxmax()
                        if abs(factor_loadings[max_factor]) >= 0.4:
                            factor_assignments[max_factor].append(idx)
                    
                    # 表示用：各因子に割り当てられた項目一覧を表示
                    st.write("各因子に割り当てられた項目（負荷量0.4以上の場合）:")
                    st.write(factor_assignments)
                    
                    # ※信頼性係数等で利用するために、最終的な表示用DataFrameも作成
                    max_loading_info = []
                    for factor, items in factor_assignments.items():
                        for item in items:
                            max_loading_info.append({
                                '項目': item,
                                '因子番号': factor,
                                '負荷量': loadings.loc[item, factor]
                            })
                    final_loadings = pd.DataFrame(max_loading_info)
                    final_loadings.set_index('項目', inplace=True)
                    
                    st.dataframe(final_loadings.style.format(formatter={'負荷量': '{:.3f}'}))
                except Exception as e:
                    st.error(f"因子負荷量の計算・表示中にエラーが発生しました: {str(e)}")

                # --- 因子間相関の表示 ---
                st.subheader("因子間相関")
                if hasattr(fa, 'corr_'):
                    try:
                        corr_matrix = fa.corr_[:n_factors, :n_factors]
                        factor_corr = pd.DataFrame(
                            corr_matrix,
                            columns=[f'Factor{i+1}' for i in range(n_factors)],
                            index=[f'Factor{i+1}' for i in range(n_factors)]
                        )
                        st.dataframe(factor_corr.round(3))
                    except Exception as e:
                        st.error(f"因子間相関の計算中にエラーが発生しました: {str(e)}")
                else:
                    st.info("※ バリマックス回転を選択した場合、因子間相関は直交を仮定するため表示されません")
                
                # --- 適合度指標（最尤法の場合：手動計算） ---
                if method == '最尤法':
                    st.subheader("適合度指標（最尤法）")
                    try:
                        # 変数数
                        p = len(selected_vars)
                        # サンプルサイズ
                        N_samples = len(df)
                        
                        # サンプル相関行列 S (p×p)
                        S = df[selected_vars].corr().values
                        
                        # モデルが再現する相関行列 Σ_model の計算
                        Lambda = fa.loadings_
                        communalities = fa.get_communalities()
                        uniquenesses = 1 - communalities
                        Psi = np.diag(uniquenesses)
                        Sigma_model = np.dot(Lambda, Lambda.T) + Psi
                        
                        # 不一致関数 F の計算
                        det_Sigma_model = np.linalg.det(Sigma_model)
                        det_S = np.linalg.det(S)
                        if det_Sigma_model <= 0 or det_S <= 0:
                            raise ValueError("行列式が非正値です。標本サイズや変数の分散を確認してください。")
                        
                        F_val = np.log(det_Sigma_model) + np.trace(np.dot(np.linalg.inv(Sigma_model), S)) - np.log(det_S) - p
                        # カイ二乗統計量の計算
                        chi_square = (N_samples - 1 - (2*p + 5)/6) * F_val
                        # 自由度の計算：df = 0.5 * [(p - m)² - p - m]
                        df_model = 0.5 * ((p - n_factors)**2 - p - n_factors)
                        # p値の計算（自由度が正の場合）
                        if df_model > 0:
                            p_value_model = 1 - chi2.cdf(chi_square, df_model)
                            # RMSEA の計算：RMSEA = sqrt(max(chi_square - df, 0) / (df*(N-1)))
                            rmsea = np.sqrt(max(chi_square - df_model, 0) / (df_model * (N_samples - 1)))
                        else:
                            p_value_model = np.nan
                            rmsea = np.nan
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("カイ二乗値:", round(chi_square, 3))
                            st.write("RMSEA:", round(rmsea, 3))
                        with col2:
                            st.write("自由度:", int(df_model))
                            st.write("p値:", round(p_value_model, 3))
                        
                        st.write("---")
                        st.write("適合度の解釈:")
                        if rmsea < 0.05:
                            st.write("・RMSEA < 0.05: 当てはまりが良好")
                        elif rmsea < 0.08:
                            st.write("・RMSEA < 0.08: 当てはまりが許容範囲")
                        elif rmsea < 0.10:
                            st.write("・RMSEA < 0.10: 当てはまりが微妙")
                        else:
                            st.write("・RMSEA ≥ 0.10: 当てはまりが不良")
                        if p_value_model > 0.05:
                            st.write("・p値 > 0.05: モデルは受容可能")
                        else:
                            st.write("・p値 ≤ 0.05: モデルの適合度に問題の可能性")
                    except Exception as e:
                        st.error(f"適合度指標の計算中にエラーが発生しました: {str(e)}")
                else:
                    st.info("""
                    ※ 適合度指標は最尤法を選択した場合のみ表示されます。
                    
                    各手法の特徴：
                    - 最尤法：正規分布を仮定し、適合度指標が利用可能
                    - 主成分法：データの分散を最大化する手法で、適合度指標は計算されない
                    - 主軸法：共通性を反復推定する手法で、適合度指標は計算されない
                    """)
                
                # --- 信頼性係数（Cronbachのα）の計算 ---
                st.subheader("信頼性係数")
                
                def calculate_cronbach_alpha(items):
                    try:
                        if len(items.columns) <= 1:
                            return np.nan
                        corr_matrix = items.corr()
                        n = len(items.columns)
                        mean_corr = (corr_matrix.values.sum() - n) / (n * (n-1))
                        alpha = (n * mean_corr) / (1 + (n-1) * mean_corr)
                        return alpha
                    except Exception as e:
                        st.error(f"Cronbachのα計算中にエラーが発生しました: {str(e)}")
                        return np.nan
                
                for i in range(n_factors):
                    mask = loadings[f'Factor{i+1}'].abs() >= 0.4
                    factor_vars = loadings.index[mask].tolist()
                    if len(factor_vars) > 1:
                        factor_items = df[factor_vars]
                        alpha = calculate_cronbach_alpha(factor_items)
                        if not np.isnan(alpha):
                            st.write(f"Factor{i+1} α係数:", round(alpha, 3))
                        else:
                            st.write(f"Factor{i+1} α係数を計算できませんでした。")
                    else:
                        st.write(f"Factor{i+1}に十分な項目がありません（α係数を計算するには最低2項目必要です）。")
                
                # --- 因子平均の計算とExcelファイルへの出力 ---
                st.subheader("因子平均の計算とExcelファイルのダウンロード")
                try:
                    # 事前に作成した factor_assignments を利用し、
                    # 各因子に割り当てられた項目の平均値を計算
                    factor_means_df = pd.DataFrame(index=df.index)
                    for factor, items in factor_assignments.items():
                        if len(items) > 0:
                            factor_means_df[f'{factor}_mean'] = df[items].mean(axis=1)
                        else:
                            factor_means_df[f'{factor}_mean'] = np.nan
                    
                    # 元のデータから、分析に使用した項目を削除
                    df_remaining = df.drop(columns=selected_vars)
                    
                    # 因子平均を結合した結果を作成
                    result_df = pd.concat([df_remaining.reset_index(drop=True),
                                           factor_means_df.reset_index(drop=True)], axis=1)
                    
                    # Excelファイルとしてバッファに保存
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        result_df.to_excel(writer, index=False, sheet_name='FactorMeans')
                    buffer.seek(0)
                    
                    st.download_button(
                        label="因子平均のExcelファイルをダウンロード",
                        data=buffer,
                        file_name="factor_means.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"因子平均の計算またはExcelファイルの作成中にエラーが発生しました: {str(e)}")

# --- フッター表示 ---
common.display_copyright()
common.display_special_thanks()
