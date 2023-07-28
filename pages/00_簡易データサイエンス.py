import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib

st.set_page_config(page_title="簡易データサイエンス", layout="wide")

st.title("簡易データサイエンス")
st.caption("Created by Daiki Ito")
st.write("")
st.subheader("ブラウザで相関分析　→　表　→　解釈まで出力できるウェブアプリです。")
st.write("iPad等でも分析を行うことができます")

st.write("")


def main():
    st.title("Excelファイルの自動可視化")
    file = st.file_uploader("Excelファイルをアップロードしてください", type=['xlsx'])

    if file is not None:
        df = pd.read_excel(file)
        st.dataframe(df)

        # List down columns for user to select
        columns = df.columns.tolist()
        selected_columns = st.multiselect("可視化したい列を選択してください", columns)

        for col in selected_columns:
            if np.issubdtype(df[col].dtype, np.number):
                # For numerical data, display histogram, box plot, and scatter plot
                st.subheader(f"ヒストグラム: {col}")
                fig, ax = plt.subplots()
                ax = sns.histplot(df[col], kde=False, bins=30)
                st.pyplot(fig)

                st.subheader(f"箱ひげ図: {col}")
                fig, ax = plt.subplots()
                ax = sns.boxplot(y=df[col])
                st.pyplot(fig)

                if len(selected_columns) > 1:
                    for scatter_col in selected_columns:
                        if scatter_col != col:
                            st.subheader(f"散布図: {col} vs {scatter_col}")
                            fig, ax = plt.subplots()
                            ax = sns.scatterplot(x=df[col], y=df[scatter_col])
                            st.pyplot(fig)

            else:
                # For non-numerical data, display bar plot and pie chart
                st.subheader(f"バープロット: {col}")
                fig, ax = plt.subplots()
                ax = sns.countplot(df[col])
                st.pyplot(fig)

                st.subheader(f"パイチャート: {col}")
                fig, ax = plt.subplots()
                df[col].value_counts().plot(kind='pie', autopct='%1.1f%%')
                st.pyplot(fig)


if __name__ == "__main__":
    main()

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9',
         'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
