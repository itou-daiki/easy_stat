import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_kmo
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
import matplotlib.pyplot as plt
import japanize_matplotlib
from PIL import Image

# ページ設定
st.set_page_config(page_title="因子分析", layout="wide")
st.title("因子分析")
st.caption("Created by Dit-Lab.(Daiki Ito)")
st.write("データから因子構造を抽出し、因子負荷量、適合度指標、信頼性係数などを算出します。")
st.write("")

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('factor_analysis_demo.xlsx', sheet_name=0)
    st.write(df.head())
else:
    if uploaded_file is not None:
        if uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.write(df.head())

if df is not None:
    # 数値変数の抽出
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    # 因子分析用の変数選択
    st.subheader("因子分析の設定")
    selected_vars = st.multiselect('分析対象の変数を選択してください', numerical_cols)
    
    if len(selected_vars) < 3:
        st.warning('少なくとも3つの変数を選択してください。')
    else:
        # 分析手法の選択
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

        # 因子数の設定
        n_factors = st.slider('抽出する因子数を選択してください', min_value=1, 
                            max_value=len(selected_vars)-1, value=3)
        
        # 分析手法の設定を変換
        method_dict = {
            '最尤法': 'ml',
            '主成分法': 'principal',
            '主軸法': 'pa'
        }
        
        rotation_dict = {
            'プロマックス回転': 'promax',
            'バリマックス回転': 'varimax'
        }
        
        # KMOとBartlettの球面性検定
        kmo_all, kmo_model = calculate_kmo(df[selected_vars])
        chi_square_value, p_value = calculate_bartlett_sphericity(df[selected_vars])
        
        st.write("KMO値:", round(kmo_model, 3))
        st.write("Bartlettの球面性検定:")
        st.write(f"カイ二乗値: {round(chi_square_value, 3)}, p値: {round(p_value, 3)}")
        
        try:
            # 因子分析の実行
            fa = FactorAnalyzer(
                rotation=rotation_dict[rotation],
                n_factors=n_factors,
                method=method_dict[method]
            )
            fa.fit(df[selected_vars])
            
            # スクリープロット
            st.subheader("スクリープロット")
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
            
            # 因子負荷量の表示
            st.subheader("因子負荷量")
            loadings = pd.DataFrame(
                fa.loadings_,
                columns=[f'Factor{i+1}' for i in range(n_factors)],
                index=selected_vars
            )
            
            # 共通性の計算
            communalities = fa.get_communalities()
            loadings['共通性'] = communalities
            
            # 各項目の最大負荷量を持つ因子とその値を特定
            max_loading_info = []
            for idx in loadings.index:
                factor_loadings = loadings.loc[idx, [f'Factor{i+1}' for i in range(n_factors)]]
                max_factor_idx = abs(factor_loadings).idxmax()
                max_loading = abs(factor_loadings[max_factor_idx])
                max_loading_info.append({
                    '項目': idx,
                    '因子番号': max_factor_idx,
                    '最大負荷量': max_loading
                })
            
            # ソート用のDataFrameを作成
            sort_df = pd.DataFrame(max_loading_info)
            sort_df = sort_df.sort_values(['因子番号', '最大負荷量'], ascending=[True, False])
            
            # ソートされた順序で新しいDataFrameを作成
            final_loadings = pd.DataFrame()
            final_loadings['項目'] = sort_df['項目']
            final_loadings['因子番号'] = sort_df['因子番号']
            for i in range(n_factors):
                final_loadings[f'Factor{i+1}'] = [loadings.loc[item, f'Factor{i+1}'] for item in final_loadings['項目']]
            final_loadings['共通性'] = [loadings.loc[item, '共通性'] for item in final_loadings['項目']]
            
            # インデックスを項目名に設定
            final_loadings.set_index('項目', inplace=True)
            
            # 因子負荷量の表示をカスタマイズ
            def style_df(val):
                try:
                    val = float(val)
                    if abs(val) >= 0.4:
                        return 'font-weight: bold'
                except:
                    pass
                return ''
            
            # スタイル適用済みのDataFrameを表示
            st.dataframe(final_loadings.style.format(formatter={
                '因子番号': lambda x: x,
                **{f'Factor{i+1}': '{:.3f}' for i in range(n_factors)},
                '共通性': '{:.3f}'
            }).applymap(style_df))
            
            # 因子間相関
            st.subheader("因子間相関")
            if hasattr(fa, 'corr_'):
                corr_matrix = fa.corr_[:n_factors, :n_factors]
                factor_corr = pd.DataFrame(
                    corr_matrix,
                    columns=[f'Factor{i+1}' for i in range(n_factors)],
                    index=[f'Factor{i+1}' for i in range(n_factors)]
                )
                st.dataframe(factor_corr.round(3))
            else:
                st.write("※ バリマックス回転を選択した場合、因子間相関は直交を仮定するため表示されません")
            
            # 適合度指標
            st.subheader("適合度指標")
            if method == '最尤法':
                try:
                    # モデルの適合度を確認
                    chi_square = fa.chi_square_
                    deg_freedom = fa.df_
                    p_value = fa.p_value_
                    
                    # RMSEAの計算
                    n_samples = len(df)
                    rmsea = np.sqrt(max(((chi_square - deg_freedom) / 
                                       ((n_samples - 1) * deg_freedom)), 0))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("RMSEA:", round(rmsea, 3))
                        st.write("カイ二乗値:", round(chi_square, 3))
                    with col2:
                        st.write("自由度:", deg_freedom)
                        st.write("p値:", round(p_value, 3))
                    
                    # 適合度の解釈
                    st.write("---")
                    st.write("適合度の解釈:")
                    if rmsea < 0.05:
                        st.write("・RMSEA < 0.05: 当てはまりが良い")
                    elif rmsea < 0.08:
                        st.write("・RMSEA < 0.08: 当てはまりが許容範囲")
                    elif rmsea < 0.10:
                        st.write("・RMSEA < 0.10: 当てはまりが微妙")
                    else:
                        st.write("・RMSEA ≥ 0.10: 当てはまりが良くない")
                    
                    if p_value > 0.05:
                        st.write("・p値 > 0.05: モデルは受容可能")
                    else:
                        st.write("・p値 ≤ 0.05: モデルの適合度に問題がある可能性")
                        
                except Exception as e:
                    st.write("""
                    適合度指標の計算でエラーが発生しました。
                    考えられる原因：
                    - サンプルサイズが小さすぎる
                    - モデルが過適合または不適合
                    - 変数間の相関が不適切
                    """)
                    st.write(f"エラー詳細: {str(e)}")
            else:
                st.write("""
                ※ 適合度指標は最尤法を選択した場合のみ表示されます。
                
                各手法の特徴：
                - 最尤法：正規分布を仮定し、適合度指標が利用可能
                - 主成分法：データの分散を最大化する手法で、適合度指標は計算されない
                - 主軸法：共通性を反復推定する手法で、適合度指標は計算されない
                """)
            
            # 信頼性係数の計算
            st.subheader("信頼性係数")
            
            def calculate_cronbach_alpha(items):
                if len(items.columns) <= 1:
                    return np.nan
                
                # 項目間の相関行列を計算
                corr_matrix = items.corr()
                n = len(items.columns)
                
                # 平均相関を計算
                mean_corr = (corr_matrix.sum().sum() - n) / (n * (n-1))
                
                # クロンバックのα係数を計算
                alpha = (n * mean_corr) / (1 + (n-1) * mean_corr)
                return alpha
            
            for i in range(n_factors):
                # 因子負荷量の絶対値が0.4以上の変数を選択
                mask = loadings[f'Factor{i+1}'].abs() >= 0.4
                factor_vars = loadings.index[mask].tolist()
                
                if len(factor_vars) > 1:  # 少なくとも2つの変数が必要
                    factor_items = df[factor_vars]
                    alpha = calculate_cronbach_alpha(factor_items)
                    if not np.isnan(alpha):
                        st.write(f"Factor{i+1} α係数:", round(alpha, 3))
                    else:
                        st.write(f"Factor{i+1} α係数を計算できませんでした。")
                else:
                    st.write(f"Factor{i+1}に十分な項目がありません（α係数を計算するには最低2項目必要です）。")

        except Exception as e:
            st.error(f"""
            分析でエラーが発生しました。以下の点を確認してください：
            - データに欠損値がないか
            - 変数間に十分な相関があるか
            - 選択した因子数が適切か
            - 最尤法の場合、データが正規分布に従っているか
            
            エラー詳細: {str(e)}
            """)

# Copyright
st.write("")
st.subheader('© 2022-2024 Dit-Lab.(Daiki Ito). All Rights Reserved.')
st.write("easyStat: Open Source for Ubiquitous Statistics")
st.write("Democratizing data, everywhere.")
st.write("")
st.write("In collaboration with our esteemed contributors:")
st.write("・Toshiyuki")
st.write("With heartfelt appreciation for their dedication and support.")