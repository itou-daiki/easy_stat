import numpy as np
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st

import common


st.set_page_config(page_title="単回帰分析", layout="wide")

# AI解釈機能の設定
gemini_api_key, enable_ai_interpretation = common.AIStatisticalInterpreter.setup_ai_sidebar()

st.title("単回帰分析")
common.display_header()
st.write("")
st.write("説明変数と目的変数の関係を単回帰分析を使用して分析する補助を行います。")
st.write("")

uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])
use_demo_data = st.checkbox('デモデータを使用')

input_df = None
if use_demo_data:
    input_df = pd.read_excel('datasets/correlation_demo.xlsx', sheet_name=0)
else:
    if uploaded_file is not None:
        if uploaded_file.type == 'text/csv':
            input_df = pd.read_csv(uploaded_file)
        else:
            input_df = pd.read_excel(uploaded_file)

feature_col = None
target_col = None
if input_df is not None:
    st.subheader('元のデータ')
    st.write(input_df)

    numerical_cols = input_df.select_dtypes(exclude=['object', 'category']).columns.tolist()

    # 説明変数の選択
    st.subheader("説明変数の選択")
    feature_col = st.selectbox('説明変数を選択してください', numerical_cols)

    # 目的変数の選択
    st.subheader("目的変数の選択")
    target_col = st.selectbox('目的変数を選択してください', numerical_cols)

    st.subheader("【分析前の確認】")
    st.write(f"{feature_col}から{target_col}の値を予測します。")

    show_graph_title = st.checkbox('グラフタイトルを表示する', value=True)  # デフォルトでチェック

    # 単回帰分析の実施
    if st.button('単回帰分析の実行'):
        if feature_col == target_col:
            st.error("説明変数と目的変数は異なるものを選択してください。")
        else:
            st.subheader('【分析結果】')
            st.write('【統計量】')

            feature = input_df[feature_col]
            target = input_df[target_col]

            # 定数項を追加
            X = sm.add_constant(feature)
            model = sm.OLS(target, X).fit()

            # 回帰係数と切片を取得
            intercept = model.params['const']
            slope = model.params[feature_col]

            # 決定係数、F値、自由度、p値を取得
            r_squared = model.rsquared
            f_value = model.fvalue
            f_pvalue = model.f_pvalue
            df_model = int(model.df_model)
            df_resid = int(model.df_resid)

            # 統計量をデータフレームにまとめる
            stats_df = pd.DataFrame({
                '指標': ['回帰係数（傾き）', '切片', '決定係数 (R²)', 'F値', '自由度（モデル）', '自由度（残差）', 'p値'],
                '値': [slope, intercept, r_squared, f_value, df_model, df_resid, f_pvalue]
            })

            # 数値をフォーマット
            def format_value(row):
                if row['指標'] in ['自由度（モデル）', '自由度（残差）']:
                    return f"{int(row['値'])}"
                elif row['指標'] == 'p値':
                    return f"{row['値']:.2f}"
                else:
                    return f"{row['値']:.2f}"

            stats_df['値'] = stats_df.apply(format_value, axis=1)

            # 統計量を表示
            st.write(stats_df)

            # 回帰直線の描画用データ作成
            x_range = np.linspace(feature.min(), feature.max(), 100)
            y_pred = intercept + slope * x_range

            # Plotly によるプロット作成
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=feature, y=target, mode='markers', name='データ'))
            fig.add_trace(go.Scatter(x=x_range, y=y_pred, mode='lines', name='回帰直線'))

            fig.update_layout(
                xaxis_title=feature_col,
                yaxis_title=target_col
            )

            if show_graph_title:
                fig.update_layout(title=f'{feature_col}と{target_col}の関係 - 単回帰分析')

            st.plotly_chart(fig)

            # 数理モデルの表示
            st.subheader(f"数理モデル: y = {slope:.2f}x + {intercept:.2f}")
            st.subheader(f"数理モデル（解釈）: {target_col} = {slope:.2f} × {feature_col} + {intercept:.2f}")
            st.subheader("")

            # AI解釈機能を追加
            if enable_ai_interpretation and gemini_api_key:
                # 回帰係数の情報を辞書形式で取得
                coefficients = {
                    'const': {'coef': intercept, 'pvalue': model.pvalues['const']},
                    feature_col: {'coef': slope, 'pvalue': model.pvalues[feature_col]}
                }

                # 調整済みR²の計算
                adj_r_squared = model.rsquared_adj

                regression_results = {
                    'r_squared': r_squared,
                    'adj_r_squared': adj_r_squared,
                    'f_statistic': f_value,
                    'f_pvalue': f_pvalue,
                    'coefficients': coefficients
                }
                common.AIStatisticalInterpreter.display_ai_interpretation(
                    api_key=gemini_api_key,
                    enabled=enable_ai_interpretation,
                    results=regression_results,
                    analysis_type='regression',
                    key_prefix='simple_regression'
                )

# フッター
common.display_copyright()
common.display_special_thanks()
