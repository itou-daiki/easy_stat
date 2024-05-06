import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
import plotly.graph_objects as go
from scipy import stats
import itertools
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'IPAexGothic'

def plot_graph(
    model: LinearRegression,
    features, 
    target, 
    feature_cols: list[str], 
    target_col: str, 
    show_graph_title: bool = False
) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    if show_graph_title:
        ax.set_title(f'{feature_cols}と{target_col}の関係 - 重回帰分析')
    
    if len(feature_cols) == 1:
        ax.set_xlabel(feature_cols[0])
        ax.set_ylabel(target_col)
        ax.scatter(features, target, color="blue")
        ax.plot(features, model.predict(features.reshape(-1, 1)), color="red")
        st.pyplot(fig)
    elif len(feature_cols) == 2:
        x1 = features[:, 0]
        x2 = features[:, 1]
        fig=plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(projection='3d')

        ax.scatter3D(x1, x2, target)
        ax.set_xlabel(feature_cols[0])
        ax.set_ylabel(feature_cols[1]) 
        ax.set_zlabel(target_col)

        mesh_x1 = np.arange(x1.min(), x1.max(), (x1.max()-x1.min())/20)
        mesh_x2 = np.arange(x2.min(), x2.max(), (x2.max()-x2.min())/20)
        mesh_x1, mesh_x2 = np.meshgrid(mesh_x1, mesh_x2)
        mesh_y = model.coef_[0] * mesh_x1 + model.coef_[1] * mesh_x2 + model.intercept_
        ax.plot_wireframe(mesh_x1, mesh_x2, mesh_y)
    
    st.pyplot(fig)

def main():
    st.set_page_config(page_title="重回帰分析アプリケーション", layout="wide")
    st.title("重回帰分析アプリケーション")
    st.caption("Created by Dit-Lab.(Daiki Ito)") 

    # ファイルのアップロード
    uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])
    use_demo_data = st.checkbox('デモデータを使用')

    if use_demo_data or uploaded_file is not None:
        if use_demo_data:
            # TODO: デモファイルを用意する 
            data = pd.read_excel('correlation_demo.xlsx', sheet_name=0)
        else:
            if uploaded_file.type == 'text/csv':
                data = pd.read_csv(uploaded_file) 
            else:
                data = pd.read_excel(uploaded_file)
        
        st.subheader('元のデータ')
        st.write(data)

        numerical_cols = data.select_dtypes(exclude=['object', 'category']).columns.tolist()
        
        # 説明変数の選択
        X_columns = st.multiselect("説明変数を選択してください", numerical_cols)
        
        # 目的変数の選択 
        y_column = st.selectbox("目的変数を選択してください", numerical_cols)
        
        is_normalization = st.checkbox('説明変数の標準化を行う', value=False)

        if 1 <= len(X_columns) <= 2:
            show_graph_title = st.checkbox('グラフタイトルを表示する', value=True)  # デフォルトでチェックされている
        
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
            
            if is_normalization:
                scaler = StandardScaler()
                X = scaler.fit_transform(X)
            
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
            coefficients = pd.DataFrame({"変数": X_poly_columns, "偏回帰係数": model.coef_, "標準化係数": model.coef_ * (X.std(axis=0) / y.std())})
            coefficients = coefficients.applymap(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)
            st.write(coefficients)
            
            if 1 <= len(X_columns) <= 2:
                plot_graph(model, X, y, X_columns, y_column, show_graph_title)
            
            # パス図の作成
            edge_traces = []
            for coef in model.coef_ * (X.std(axis=0) / y.std()):
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
                text=[f"{coef:.2f}<br>{'**' if abs(coef) >= 0.2 else '*' if abs(coef) >= 0.1 else ''}" for coef in model.coef_ * (X.std(axis=0) / y.std())],
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

    # Copyright
    st.subheader('© 2022-2024 Dit-Lab.(Daiki Ito). All Rights Reserved.')
    st.write("easyStat: Open Source for Ubiquitous Statistics")
    st.write("Democratizing data, everywhere.")
    st.write("")
    st.subheader("In collaboration with our esteemed contributors:")
    st.write("・Toshiyuki")
    st.write("With heartfelt appreciation for their dedication and support.")

if __name__ == "__main__":
    main()