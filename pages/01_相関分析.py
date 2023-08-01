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
                r = round(df.corr().iat[v1, v2], 2)
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


# Set page config
st.set_page_config(page_title="相関分析", layout="wide")

# Application title
st.title("相関分析ウェブアプリ")

# Application description
st.write("このウェブアプリケーションでは、アップロードしたデータセットの特定の変数間の相関分析を簡単に実行できます。\
          さらに、相関係数のヒートマップを生成し、相関の強さを視覚的に確認できます。")

# ... (the rest of your code follows)


st.header("データアップロード")
st.write("ExcelまたはCSVファイルをアップロードしてください。数値データの列のみが分析に使用できます。")

# Excelデータの例
image = Image.open('correlation.png')
st.image(image, caption='Excelデータの例')

# xlsxまたはcsvファイルのアップロード
upload_files = st.file_uploader("ファイルアップロード", type=['xlsx', 'csv'])

if upload_files:
    try:
        # xlsxまたはcsvファイルの読み込み → データフレームにセット
        if upload_files.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            df = pd.read_excel(upload_files, sheet_name=0)
        elif upload_files.type == 'text/csv':
            df = pd.read_csv(upload_files)
        # 欠損値を含むレコードを削除
        df.dropna(how='any', inplace=True)
        st.success('データの読み込みに成功しました。')
    except Exception as e:
        st.error(f'エラーが発生しました: {e}')
else:
    # デモ用ファイル
    df = pd.read_excel('correlation_demo.xlsx', sheet_name=0)
    st.info('デモデータがロードされました。')

# データフレーム表示ボタン
if st.checkbox('データフレームの表示（クリックで開きます）'):
    st.dataframe(df, width=0)

# 変数選択フォーム
with st.form(key='variable_form'):
    st.subheader("分析に使用する変数の選択")

    # 変数のセット
    a = df.columns.tolist()

    # 複数選択
    Variable = st.multiselect('変数を選択（複数選択可）', a)

    # 確認ボタンの表示
    CHECK_btn = st.form_submit_button('確認')

# 分析前の確認フォーム
with st.form(key='check_form'):
    if CHECK_btn:
        st.subheader('【分析前の確認】')

        for v in Variable:
            st.write(f'● 【{v}】')

        st.write('上記の変数間に相関関係があるか分析します。')

        # 分析実行ボタンの表示
        ANALYZE_btn = st.form_submit_button('分析実行')

# 分析結果表示フォーム
with st.form(key='analyze_form'):
    if ANALYZE_btn:
        st.subheader('【分析結果】')

        # 選択した変数から作業用データフレームのセット
        dfAv = df[Variable]

        st.write('【相関分析】')
        st.dataframe(dfAv.corr(), width=0)

        # Adding a heatmap of correlation
        st.write('【相関行列のヒートマップ】')
        fig, ax = plt.subplots()
        sns.heatmap(dfAv.corr(), annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)

        if st.checkbox('【相関係数( r )の判定】'):
            st.write('0.7 ≦ r ≦ 1.0 ・・・強い正の相関')
            st.write('0.4 ≦ r ≦ 0.7 ・・・正の相関')
            st.write('0.2 ≦ r ≦ 0.4 ・・・弱い正の相関')
            st.write('-0.2 ≦ r ≦ 0.2 ・・・相関なし')
            st.write('-0.4 ≦ r ≦ -0.2 ・・・弱い負の相関')
            st.write('-0.7 ≦ r ≦ -0.4 ・・・負の相関')
            st.write('-1.0 ≦ r ≦ -0.7 ・・・強い負の相関')

        st.write('')
        st.write('【分析結果の解釈】')
        # Improved correlation interpretation
        interpret_correlation(dfAv, Variable)

        ANALYZE_btn = st.form_submit_button('OK')

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9',
         'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
