import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pandas as pd

from sklearn import preprocessing
from sklearn.linear_model import LinearRegression

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
        ax.plot(features, target_pred, color="red")
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
                

st.set_page_config(page_title="重回帰分析", layout="wide")

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

feature_col = None
target_col = None
if input_df is not None:
    st.subheader('元のデータ')
    st.write(input_df)

    numerical_cols = input_df.select_dtypes(exclude=['object', 'category']).columns.tolist()

    # 説明変数の選択
    st.subheader("説明変数の選択")
    feature_cols = st.multiselect('説明変数を選択してください', numerical_cols)

    # 目的変数の選択
    st.subheader("目的変数の選択")
    target_col = st.selectbox('目的変数を選択してください', numerical_cols)

    st.subheader("【分析前の確認】")
    st.write(f"{feature_cols}から{target_col}の値を予測します。")

    is_normalizataion = st.checkbox('説明変数の標準化を行う', value=False)

    if 1 <= len(feature_cols) <= 2:
        show_graph_title = st.checkbox('グラフタイトルを表示する', value=True)  # デフォルトでチェックされている

    # 単回帰分析の実施
    if st.button('重回帰分析の実行'):
        if len(feature_cols) == 0:
             st.error("説明変数を少なくとも１つは選択してください。")
        elif target_col in feature_cols:
             st.error("目的変数は説明変数に含まれていないものを選択してください。")
        else:
            st.subheader('【分析結果】')
            st.write('【要約統計量】')

            features = input_df[feature_cols].to_numpy()
            target = input_df[target_col]

            if is_normalizataion:
                # 標準化
                sscaler = preprocessing.StandardScaler()
                sscaler.fit(features)
                features = sscaler.transform(features)

            model = LinearRegression()
            model.fit(features, target)
            target_pred = model.predict(features)

            if len(feature_cols) <= 2:
                plot_graph(model, features, target, feature_cols, target_col, show_graph_title)

            coefs_str = "編回帰係数:\n"
            for i, coef in enumerate(model.coef_):
                coefs_str += f"- x{i} = {feature_cols[i]},  a{i} = {coef}\n"

            st.write(coefs_str)
            st.write(f"切片: {model.intercept_}")
            st.write("")

# Copyright
st.subheader('© 2022-2024 Dit-Lab.(Daiki Ito). All Rights Reserved.')
st.write("easyStat: Open Source for Ubiquitous Statistics")
st.write("Democratizing data, everywhere.")
st.write("")
st.subheader("In collaboration with our esteemed contributors:")
st.write("・Toshiyuki")
st.write("With heartfelt appreciation for their dedication and support.")
