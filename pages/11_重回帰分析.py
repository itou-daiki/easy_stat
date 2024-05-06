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
    st.title("重回帰分析アプリケーション")
    
    # ファイルのアップロード
    uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")
    
    if uploaded_file is not None:
        # データの読み込み
        data = pd.read_csv(uploaded_file)
        
        # 説明変数と目的変数の選択
        X_columns = st.multiselect("説明変数を選択してください", data.columns)
        y_column = st.selectbox("目的変数を選択してください", data.columns)
        
        if len(X_columns) > 0 and y_column:
            X = data[X_columns]
            y = data[y_column]
            
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