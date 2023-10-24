import streamlit as st
import pandas as pd
import scipy.stats as stats
import plotly.express as px
import matplotlib.pyplot as plt
import japanize_matplotlib
from PIL import Image

st.set_page_config(page_title="カイ２乗分析", layout="wide")

st.title("カイ２乗分析ウェブアプリ")

st.write("度数の偏りを分析することができます")

# 分析のイメージ
image = Image.open('correlation.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('chi_square_demo.xlsx', sheet_name=0)
    st.write(df.head())
else:
    if uploaded_file is not None:
        if uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
            st.write(df.head())
        else:
            df = pd.read_excel(uploaded_file)
            st.write(df.head())

if df is not None:
    # カテゴリ変数の抽出
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # カテゴリ変数の選択
    st.subheader("カテゴリ変数の選択")
    selected_col1 = st.selectbox('変数1を選択してください', categorical_cols, key='select1')
    categorical_cols.remove(selected_col1)  # 選択済みの変数をリストから削除
    selected_col2 = st.selectbox('変数2を選択してください', categorical_cols, key='select2')

    # 選択した変数の度数分布のバープロット
    for col in [selected_col1, selected_col2]:
        st.subheader(f"【{col}】 の度数分布")
        fig = px.bar(df, x=df[col].value_counts().index, y=df[col].value_counts().values, labels={df[col].name: '度数'})
        st.plotly_chart(fig)

    # クロス表の作成と表示
    crosstab = pd.crosstab(df[selected_col1], df[selected_col2])
    st.subheader(f'【{selected_col1}】 と 【{selected_col2}】 のクロス表')
    st.write(crosstab)

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')