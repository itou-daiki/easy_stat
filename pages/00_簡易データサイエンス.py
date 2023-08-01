import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib

import matplotlib as mpl
# フォントのプロパティを設定
font_prop = mpl.font_manager.FontProperties(fname="ipaexg.ttf")
# Matplotlibのデフォルトのフォントを変更
mpl.rcParams['font.family'] = font_prop.get_name()
sns.set(font='ipaexg.ttf')

st.set_page_config(page_title="簡易データサイエンス", layout="wide")

st.title("簡易データサイエンス")
st.caption("Created by Daiki Ito")
st.write("")
st.subheader("ブラウザで簡易的なデータサイエンスが実行できるウェブアプリです。")
st.write("iPad等でも分析を行うことができます")

st.write("")

# デモ用ファイル
demo_df = pd.read_excel('data_science_demo.xlsx', sheet_name=0)

# データフレーム表示ボタン
if st.checkbox('データフレームの表示（クリックで開きます）'):
    st.dataframe(demo_df, width=0)

# データのアップロード
def upload_data():
    file = st.file_uploader("ExcelファイルまたはCSVファイルをアップロードしてください", type=['xlsx', 'csv'])

    # ファイルがアップロードされていない場合、デモ用データを使用
    if file is None:
        df = demo_df
    else:
        if file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(file)
        elif file.type == "text/csv":
            df = pd.read_csv(file)
        else:
            st.error("アップロードされたファイルの形式がサポートされていません。")
            return

    return df

# データの分析
def analyze_data(df):
    st.dataframe(df)
    st.write("データの基本情報")
    st.write(df.describe())

    st.write("欠損値の数")
    st.write(df.isnull().sum())

    # List down columns for user to select
    columns = df.columns.tolist()
    selected_columns = st.multiselect("可視化したい列を選択してください", columns)

    # Visualization
    # ...

    # Correlation matrix and heatmap for numerical data
    if st.checkbox("数値データの相関行列とヒートマップの表示"):
        # Select only numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        st.write(df[numerical_cols].corr())
        fig, ax = plt.subplots()
        sns.heatmap(df[numerical_cols].corr(), annot=True, fmt=".2f", cmap='coolwarm', cbar=True, square=True, ax=ax)
        st.pyplot(fig)

if __name__ == "__main__":
    df = upload_data()
    if df is not None:
        analyze_data(df)

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9',
         'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
