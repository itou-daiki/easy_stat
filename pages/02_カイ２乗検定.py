import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.express as px
import plotly.figure_factory as ff
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
    st.subheader(f'【{selected_col1}】 と 【{selected_col2}】 の度数分布')
    
    # クロス表の作成
    crosstab = pd.crosstab(df[selected_col1], df[selected_col2])

    # クロス表を長い形式に変換
    crosstab_long = crosstab.reset_index().melt(id_vars=selected_col1, value_name='度数')

    # プロットの作成
    fig = px.bar(
        crosstab_long,
        x=selected_col2,
        y='度数',
        color=selected_col1,
        barmode='group',
        labels={selected_col1: selected_col1, selected_col2: selected_col2, '度数': '度数'},
        title=f'【{selected_col1}】 と 【{selected_col2}】 の度数分布'
    )

    # グラフの表示
    st.plotly_chart(fig)

    # クロス表の作成と表示
    # crosstab = pd.crosstab(df[selected_col1], df[selected_col2])
    st.subheader(f'【{selected_col1}】 と 【{selected_col2}】 のクロス表')

    # カイ２乗検定の実行
    chi2, p_value, dof, expected = stats.chi2_contingency(crosstab)

    # 有意差を確認するための残差の計算
    residuals = (crosstab - expected) / np.sqrt(expected)

    # 有意水準0.05でのz値の閾値
    threshold = stats.norm.ppf(1 - 0.05 / 2)

    # 有意に差が出ているセルのマスキング
    mask_significant = residuals.abs() > threshold

    # セルに色を付ける
    colors = mask_significant.applymap(lambda x: 'background-color: yellow' if x else '')

    # ヒートマップの作成と表示
    st.write('有意に差が出ているセルは黄色で表示されます:')
    st.write(crosstab.style.apply(lambda x: colors, axis=None))

    # カイ二乗検定の結果を表示
    st.subheader('カイ二乗検定の結果')
    st.write(f'カイ二乗統計量: {chi2:.2f}')
    st.write(f'P値: {p_value:.2f}')

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')