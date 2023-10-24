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
    selected_cols = st.multiselect('カテゴリ変数を選択してください', categorical_cols)

    if len(selected_cols) > 0:
        for col in selected_cols:
            st.subheader(f"{col} の度数分布")
            # 度数分布のバープロット (Plotlyを使用)
            fig = px.bar(df, x=df[col].value_counts().index, y=df[col].value_counts().values, labels={df[col].name: '度数'})
            st.plotly_chart(fig)

            # カイ２乗分析
            crosstab = pd.crosstab(df[col], columns="count")
            chi2, p_value, dof, expected = stats.chi2_contingency(crosstab)
            
            # 結果をデータフレームに格納
            results_df = pd.DataFrame({
                "項目": ["カイ二乗統計量", "P値", "自由度"],
                "値": [chi2, p_value, dof]
            })

            # クロス表を表示
            st.write('クロス表:')
            st.write(crosstab)
            
            # 結果のデータフレームを表示
            st.write('カイ二乗分析結果:')
            st.dataframe(results_df)
            
            # 有意差がある場合は、明示的に表示
            if p_value < 0.05:
                st.markdown(f'### {col} には **有意差** があります!')
    else:
        st.warning('少なくとも1つのカテゴリ変数を選択してください。')

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')