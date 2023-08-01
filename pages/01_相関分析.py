import streamlit as st
import pandas as pd
import japanize_matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

import matplotlib as mpl

# フォントのプロパティを設定
font_prop = mpl.font_manager.FontProperties(fname="ipaexg.ttf")
# Matplotlibのデフォルトのフォントを変更
mpl.rcParams['font.family'] = font_prop.get_name()

# Function for interpreting correlation
def interpret_correlation(df, variables):
    for v1 in variables:
        for v2 in variables:
            if v1 != v2:
                r = round(df.corr().loc[v1, v2], 2)
                if 0.7 <= r <= 1.0:
                    st.markdown(f'【{v1}】と【{v2}】の間には「強い正の相関」がある（ r = {r} )')
                elif 0.4 <= r < 0.7:
                    st.markdown(f'【{v1}】と【{v2}】の間には「正の相関」がある（ r = {r} )')
                elif 0.2 <= r < 0.4:
                    st.markdown(f'【{v1}】と【{v2}】の間には「弱い正の相関」がある（ r = {r} )')
                elif -0.2 <= r < 0.2:
                    st.write(f'【{v1}】と【{v2}】の間には「相関がない」（ r = {r} )')
                elif -0.4 <= r < -0.2:
                    st.markdown(f'【{v1}】と【{v2}】の間には「弱い負の相関」がある（ r = {r} )')
                elif -0.7 <= r < -0.4:
                    st.markdown(f'【{v1}】と【{v2}】の間には「負の相関」がある（ r = {r} )')
                elif -1.0 <= r < -0.7:
                    st.markdown(f'【{v1}】と【{v2}】の間には「強い負の相関」がある（ r = {r} )')

st.set_page_config(page_title="相関分析", layout="wide")

st.title("相関分析ウェブアプリ")

st.write("このウェブアプリケーションでは、アップロードしたデータセットの特定の変数間の相関分析を簡単に実行できます。\
          さらに、相関係数のヒートマップを生成し、相関の強さを視覚的に確認できます。")

# Data upload form
with st.form(key='data_upload_form'):
    st.header("データアップロード")
    st.write("ExcelまたはCSVファイルをアップロードしてください。数値データの列のみが分析に使用できます。")

    image = Image.open('correlation.png')
    st.image(image, caption='Excelデータの例')

    upload_files = st.file_uploader("ファイルアップロード", type=['xlsx', 'csv'])

    if upload_files:
        try:
            if upload_files.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                df = pd.read_excel(upload_files, sheet_name=0)
            elif upload_files.type == 'text/csv':
                df = pd.read_csv(upload_files)
            df.dropna(how='any', inplace=True)
            st.success('データの読み込みに成功しました。')
        except Exception as e:
            st.error(f'エラーが発生しました: {e}')
    else:
        df = pd.read_excel('correlation_demo.xlsx', sheet_name=0)
        st.info('デモデータがロードされました。')

    if st.checkbox('データフレームの表示'):
        st.dataframe(df)

    st.subheader("分析に使用する変数の選択")
    a = df.columns.tolist()
    Variable = st.multiselect('変数を選択（複数選択可）', a)

    # 確認ボタンの表示
    confirm_button = st.form_submit_button('確認')

# Analysis results
if confirm_button:
    st.subheader('【分析結果】')
    dfAv = df[Variable]

    with st.expander('相関分析'):
        st.dataframe(dfAv.corr())

    with st.expander('相関行列のヒートマップ'):
        fig, ax = plt.subplots()
        sns.heatmap(dfAv.corr(), annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)

    if st.checkbox('相関係数( r )の判定'):
        st.write('0.7 ≦ r ≦ 1.0 ・・・強い正の相関')
        st.write('0.4 ≦ r ≦ 0.7 ・・・正の相関')
        st.write('0.2 ≦ r ≦ 0.4 ・・・弱い正の相関')
        st.write('-0.2 ≦ r ≦ 0.2 ・・・相関なし')
        st.write('-0.4 ≦ r ≦ -0.2 ・・・弱い負の相関')
        st.write('-0.7 ≦ r ≦ -0.4 ・・・負の相関')
        st.write('-1.0 ≦ r ≦ -0.7 ・・・強い負の相関')

    st.subheader('【分析結果の解釈】')
    interpret_correlation(dfAv, Variable)

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
