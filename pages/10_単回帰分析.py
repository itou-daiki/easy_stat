import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression


plt.rcParams['font.family'] = 'IPAexGothic'

st.set_page_config(page_title="単回帰分析", layout="wide")

st.title("単回帰分析")
st.caption("Created by Dit-Lab.(Daiki Ito)")
st.write("")
st.write("説明変数と目的変数の関係を単回帰分析を使用して分析する補助を行います。")

st.write("")

# TODO 共通化
uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])
use_demo_data = st.checkbox('デモデータを使用')

input_df = None
if use_demo_data:
     # TODO デモファイルを用意する
     input_df = pd.read_excel('correlation_demo.xlsx', sheet_name=0)
else:
    if uploaded_file is not None:
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
    feature_col = st.selectbox('説明変数を選択してください', numerical_cols)

    # 目的変数の選択
    st.subheader("目的変数の選択")
    target_col = st.selectbox('目的変数を選択してください', numerical_cols)

    st.subheader("【分析前の確認】")
    st.write(f"{feature_col}から{target_col}の値を予測します。")

    show_graph_title = st.checkbox('グラフタイトルを表示する', value=True)  # デフォルトでチェックされている

    # 単回帰分析の実施
    if st.button('単回帰分析の実行'):
        if feature_col == target_col:
             st.error("説明変数と目的変数は異なるものを選択してください。")
        else:
            st.subheader('【分析結果】')
            st.write('【要約統計量】')

            feature = input_df[feature_col].to_numpy().reshape(-1, 1)
            target = input_df[target_col]

            model = LinearRegression()
            model.fit(feature, target)
            target_pred = model.predict(feature)

            fig, ax = plt.subplots(figsize=(8, 6))
            if show_graph_title:
                ax.set_title(f'{feature_col}と{target_col}の関係 - 単回帰分析')
            ax.set_xlabel(feature_col)
            ax.set_ylabel(target_col)
            ax.scatter(feature, target, color="blue")
            ax.plot(feature, target_pred, color="red")
            st.pyplot(fig)

            st.write(f"回帰係数: {model.coef_[0]}")
            st.write(f"切片: {model.intercept_}")
            st.write("")


st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
# Copyright
st.subheader('© 2022-2024 Dit-Lab.(Daiki Ito). All Rights Reserved.')
st.write("easyStat: Open Source for Ubiquitous Statistics")
st.write("Democratizing data, everywhere.")
st.write("")
st.subheader("In collaboration with our esteemed contributors:")
st.write("・Toshiyuki")
st.write("With heartfelt appreciation for their dedication and support.")
