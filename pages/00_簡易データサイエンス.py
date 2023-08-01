import streamlit as st
import pandas as pd
import numpy as np
import japanize_matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

import matplotlib as mpl
font_prop = mpl.font_manager.FontProperties(fname="ipaexg.ttf")
mpl.rcParams['font.family'] = font_prop.get_name()
sns.set(font='ipaexg.ttf')

st.set_page_config(page_title="簡易データサイエンス", layout="wide")

st.title("簡易データサイエンス")
st.caption("Created by Daiki Ito")
st.write("")
st.subheader("ブラウザで簡易的なデータサイエンスが実行できるウェブアプリです。")
st.write("iPad等でも分析を行うことができます")
st.write("")

demo_df = pd.read_excel('data_science_demo.xlsx', sheet_name=0)

def upload_data():
    file = st.file_uploader("ExcelファイルまたはCSVファイルをアップロードしてください", type=['xlsx', 'csv'])
    use_demo = st.checkbox("デモ用データを使用する")

    if file is None and not use_demo:
        st.warning("ファイルがアップロードされていません。")
        return None

    if use_demo:
        df = demo_df
    else:
        try:
            if file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                df = pd.read_excel(file)
            elif file.type == "text/csv":
                df = pd.read_csv(file)
            else:
                st.error("アップロードされたファイルの形式がサポートされていません。")
                return None
        except Exception as e:
            st.error(f"データの読み込みに失敗しました: {e}")
            return None

    return df

def analyze_data(df):
    st.subheader('データの分析')
    with st.expander('データフレームの表示'):
        st.dataframe(df, width=0)

    with st.expander("データの基本情報"):
        st.write(df.describe())

    with st.expander("欠損値の数"):
        st.write(df.isnull().sum())

    columns = df.columns.tolist()
    selected_columns = st.multiselect("可視化したい列を選択してください", columns)

    if selected_columns:
        for col in selected_columns:
            st.subheader(f"{col}の可視化")
            if df[col].dtype in [np.number]:
                fig, ax = plt.subplots()
                df[col].hist(ax=ax)
                st.pyplot(fig)
            else:
                st.write(f"{col}は数値データではないため、可視化できません。")

    if st.checkbox("数値データの相関行列とヒートマップの表示"):
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        st.write(df[numerical_cols].corr())
        fig, ax = plt.subplots()
        sns.heatmap(df[numerical_cols].corr(), annot=True, fmt=".2f", cmap='coolwarm', cbar=True, square=True, ax=ax)
        st.pyplot(fig)

if __name__ == "__main__":
    df = upload_data()
    if df is not None:
        analyze_data(df)

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
