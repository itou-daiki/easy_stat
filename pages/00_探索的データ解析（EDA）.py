import streamlit as st
import pandas as pd
import pygwalker as pyg
import matplotlib.pyplot as plt
import japanize_matplotlib
import streamlit.components.v1 as components

st.set_page_config(page_title="探索的データ解析（EDA）", layout="wide")

st.title("探索的データ解析（EDA）")
st.caption("Created by Daiki Ito")
st.write("")
st.subheader("簡易的な探索的データ解析（EDA）が実行できます")
st.write("iPad等でも分析を行うことができます")
st.write("")

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('eda_demo.xlsx', sheet_name=0)
    st.write(df.head())
else:
    if uploaded_file is not None:
        if uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
            st.write(df.head())
        else:
            df = pd.read_excel(uploaded_file)
            st.write(df.head())

# Graphic Walker 操作（メインパネル）
if df is not None:
    try:
        output = pyg.walk(df, env='Streamlit')
        st.write(output)
    except Exception as e:
        st.write(f'エラー: {e}')

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')