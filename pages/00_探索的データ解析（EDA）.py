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

if df is not None:
    # カテゴリ変数と数値変数の選択
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    numerical_cols = df.select_dtypes(exclude=['object', 'category']).columns.tolist()

    # 要約統計量表示
    st.subheader('要約統計量')
    summary_df = df.describe(include='all').transpose()
    st.write(summary_df)

    # 可視化
    st.subheader('可視化')

    # 変数選択
    selected_vars = st.multiselect('変数を選択してください:', df.columns.tolist(), default=df.columns.tolist())

    if len(selected_vars) == 2:
        var1, var2 = selected_vars
        
        # カテゴリ×カテゴリ
        if var1 in categorical_cols and var2 in categorical_cols:
            cross_tab = pd.crosstab(df[var1], df[var2])
            fig = px.imshow(cross_tab, labels=dict(color="Count"), title=f'個数のカウント: {var1} vs {var2}')
            st.plotly_chart(fig)
        
        # 数値×数値
        elif var1 in numerical_cols and var2 in numerical_cols:
            fig = px.scatter(df, x=var1, y=var2, title=f'散布図: {var1} vs {var2}')
            st.plotly_chart(fig)
            st.write(f'相関係数: {df[var1].corr(df[var2]):.2f}')
        
        # カテゴリ×数値
        else:
            if var1 in categorical_cols:
                cat_var, num_var = var1, var2
            else:
                cat_var, num_var = var2, var1
            
            fig = px.box(df, x=cat_var, y=num_var, title=f'棒グラフ: {cat_var} vs {num_var}')
            st.plotly_chart(fig)

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')