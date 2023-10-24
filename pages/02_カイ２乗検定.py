import streamlit as st
import pandas as pd
import scipy.stats as stats
import seaborn as sns
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
            # 度数分布のバープロット
            plt.figure(figsize=(8, 6))
            sns.countplot(data=df, x=col)
            st.pyplot(plt)

            # カイ２乗分析
            crosstab = pd.crosstab(df[col], columns="count")
            chi2, p_value, dof, expected = stats.chi2_contingency(crosstab)
            
            # 結果をデータフレームに格納
            results_df = pd.DataFrame({
                "項目": ["カイ二乗統計量", "P値", "自由度"],
                "値": [chi2, p_value, dof]
            })
            
            # 結果のデータフレームを表示
            st.dataframe(results_df)
    else:
        st.warning('少なくとも1つのカテゴリ変数を選択してください。')