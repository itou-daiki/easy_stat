import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import PolynomialFeatures
import plotly.graph_objects as go
from scipy import stats
import itertools

def main():
    st.title("重回帰分析")
    st.caption("Created by Dit-Lab.(Daiki Ito)")
    st.write("")
    st.write("説明変数と目的変数の関係を重回帰分析を使用して分析する補助を行います。")

    st.write("")

    uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])
    use_demo_data = st.checkbox('デモデータを使用')

    input_df = None
    if use_demo_data:
        # TODO デモファイルを用意する
        input_df = pd.read_excel('correlation_demo.xlsx', sheet_name=0)
    #else:
    elif uploaded_file is not None:
        print(uploaded_file.type)
        if uploaded_file.type == 'text/csv':
            input_df = pd.read_csv(uploaded_file)
        else:
            input_df = pd.read_excel(uploaded_file)
            
    if input_df is not None:
        st.subheader('元のデータ')
        st.write(input_df)

        numerical_cols = input_df.select_dtypes(exclude=['object', 'category']).columns.tolist()
    
        # 説明変数と目的変数の選択
        st.subheader("説明変数の選択")
        X_columns = st.multiselect("説明変数を選択してください", numerical_cols)
        st.subheader("目的変数の選択")
        y_column = st.selectbox("目的変数を選択してください", numerical_cols)
        
        st.subheader("【分析前の確認】")
        st.write(f"{X_columns}から{y_column}の値を予測します。")
        
        # 単回帰分析の実施
        if st.button('重回帰分析の実行'):
        
            if len(X_columns) > 0 and y_column:
                X = input_df[X_columns]
                y = input_df[y_column]
                
                # 交互作用項の生成（総当たり）
                interaction_terms = []
                for i in range(2, len(X_columns) + 1):
                    for combination in itertools.combinations(X_columns, i):
                        term = " × ".join(combination)
                        X[term] = X[list(combination)].prod(axis=1)
                        interaction_terms.append(term)
                
                X_poly_columns = X.columns
                
                # 重回帰分析の実行
                model = LinearRegression()
                model.fit(X, y)
                
                # 結果の表示
                st.subheader("重回帰分析の結果")
                r2 = r2_score(y, model.predict(X))
                
                # F値、自由度、p値の計算
                n = len(y)
                k = len(X_poly_columns)
                f_value = (r2 / k) / ((1 - r2) / (n - k - 1))
                df_model = k
                df_resid = n - k - 1
                p_value = stats.f.sf(f_value, df_model, df_resid)
                
                # 決定係数、F値、自由度、p値をデータフレームで表示
                summary_df = pd.DataFrame({
                    '指標': ['決定係数', 'F値', '自由度', 'p値'],
                    '値': [round(r2, 2), round(f_value, 2), f"{df_model}, {df_resid}", round(p_value, 2)]
                })
                st.write(summary_df)
                
                st.subheader("偏回帰係数と標準化係数")
                coefficients = pd.DataFrame({"変数": X_poly_columns, "偏回帰係数": model.coef_, "標準化係数": model.coef_ * (X.std() / y.std())})
                coefficients = coefficients.applymap(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)
                st.write(coefficients)
                
                # パス図の作成
                edge_traces = []
                for coef in model.coef_ * (X.std() / y.std()):
                    edge_traces.append(go.Scatter(
                        x=[0.25, 0.25, 0.4, -0.1, -0.1, -0.35],
                        y=[0.6, 0.4, 0, 0.6, 0.4, 0],
                        mode='lines',
                        line=dict(color='rgba(0,0,255,0.5)', width=abs(coef) * 5),
                        hoverinfo='none',
                        showlegend=False
                    ))
                
                anno_trace = go.Scatter(
                    x=[0.30, 0.30, 0.4, -0.15, -0.15, -0.35],
                    y=[0.65, 0.35, 0, 0.65, 0.35, 0],
                    mode='text',
                    text=[f"{coef:.2f}<br>{'**' if abs(coef) >= 0.2 else '*' if abs(coef) >= 0.1 else ''}" for coef in model.coef_ * (X.std() / y.std())],
                    textposition='top center',
                    hoverinfo='none',
                    showlegend=False
                )
                
                rect_trace = go.Scatter(
                    x=[-0.5, 0.5, 0.5, -0.5, -0.5],
                    y=[0.8, 0.8, -0.2, -0.2, 0.8],
                    mode='lines',
                    fill='toself',
                    fillcolor='rgba(255, 255, 255, 1.0)',
                    line=dict(color='black', width=1),
                    hoverinfo='none',
                    showlegend=False
                )
                
                text_trace = go.Scatter(
                    x=[-0.45, -0.45, 0.35, 0.35, -0.45],
                    y=[0.7, 0.5, 0.7, 0.5, -0.1],
                    mode='text',
                    text=X_poly_columns.tolist() + [y_column],
                    hoverinfo='none',
                    showlegend=False
                )
                
                fig = go.Figure(data=[rect_trace] + edge_traces + [anno_trace, text_trace])
                
                fig.update_layout(
                    title_text=f"パス図 (R={np.sqrt(r2):.2f}, F<sub>{df_model, df_resid}</sub>={f_value:.3f}**)",
                    font_size=10,
                    showlegend=False,
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='white'
                )
                
                st.plotly_chart(fig)

if __name__ == "__main__":
    main()


st.write('')
st.write('')
st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
# Copyright
st.subheader('© 2022-2024 Dit-Lab.(Daiki Ito). All Rights Reserved.')
st.write("easyStat: Open Source for Ubiquitous Statistics")
st.write("Democratizing data, everywhere.")
st.write("")
st.subheader("In collaboration with our esteemed contributors:")
st.write("・Toshiyuki")
st.write("With heartfelt appreciation for their dedication and support.")