import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import japanize_matplotlib

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

# カテゴリ変数と数値変数の選択
st.sidebar.header('パラメータ設定')
selected_categorical = st.sidebar.multiselect('カテゴリ変数を選択してください', df.select_dtypes(include=['object']).columns.tolist())
selected_numerical = st.sidebar.multiselect('数値変数を選択してください', df.select_dtypes(include=['number']).columns.tolist())

# サマリー（要約統計量）の表示
st.subheader('サマリー（要約統計量）')
if selected_categorical:
    st.write(df[selected_categorical].describe(include='object'))
if selected_numerical:
    st.write(df[selected_numerical].describe())

# 可視化
if len(selected_categorical) == 2 and len(selected_numerical) == 0:
    # カテゴリ変数とカテゴリ変数の場合
    count_df = df.groupby(selected_categorical).size().reset_index(name='count')
    fig = px.bar(count_df, x=selected_categorical[0], y='count', color=selected_categorical[1], title=f'{selected_categorical[0]} vs {selected_categorical[1]}')
    st.plotly_chart(fig)

elif len(selected_categorical) == 0 and len(selected_numerical) == 2:
    # 数値変数と数値変数の場合
    fig = px.scatter(df, x=selected_numerical[0], y=selected_numerical[1], title=f'{selected_numerical[0]} vs {selected_numerical[1]}')
    st.plotly_chart(fig)
    st.write(f'相関係数: {df[selected_numerical].corr().iloc[0, 1]:.2f}')

elif len(selected_categorical) == 1 and len(selected_numerical) == 1:
    # カテゴリ変数と数値変数の場合
    fig = px.bar(df, x=selected_categorical[0], y=selected_numerical[0], title=f'{selected_categorical[0]} vs {selected_numerical[0]}')
    st.plotly_chart(fig)

# その他のEDA機能
st.sidebar.subheader('その他のEDA機能')
if st.sidebar.checkbox('ヒストグラムを表示'):
    st.subheader('ヒストグラム')
    fig = px.histogram(df, nbins=50)
    st.plotly_chart(fig)

if st.sidebar.checkbox('欠損値の確認'):
    st.subheader('欠損値の確認')
    missing_df = df.isnull().sum().reset_index()
    missing_df.columns = ['Column', 'Missing Values']
    st.write(missing_df)

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')