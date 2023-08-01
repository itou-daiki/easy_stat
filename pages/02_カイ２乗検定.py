
import streamlit as st
import pandas as pd
from scipy.stats import chi2_contingency
from PIL import Image

st.set_page_config(page_title="カイ二乗検定", layout="wide")

st.title("カイ二乗検定")
st.caption("Created by Daiki Ito")
st.write("")
st.subheader("ブラウザでカイ二乗検定　→　表　→　解釈まで出力できるウェブアプリです。")
st.write("iPad等でも分析を行うことができます")
st.write("")

st.subheader("【注意事項】")
st.write("Excelファイルに不備があるとエラーが出ます")
st.write('<span style="color:blue">デフォルトでデモ用データの分析ができます。</span>',
         unsafe_allow_html=True)
st.write(
    '<span style="color:blue">ファイルをアップせずに「データフレームの表示」ボタンを押すと　'
    'デモ用のデータを確認できます。</span>',
    unsafe_allow_html=True)
st.write('<span style="color:red">欠損値を含むレコード（行）は自動で削除されます。</span>',
         unsafe_allow_html=True)

# デモ用ファイル
df = pd.read_excel('chi_square_demo.xlsx', sheet_name=0)

# xlsx, csvファイルのアップロード
upload_files = st.file_uploader("ファイルアップロード", type=['xlsx', 'csv'])

# xlsx, csvファイルの読み込み → データフレームにセット
if upload_files:
    # dfを初期化
    df.drop(range(len(df)))
    # ファイルの拡張子によって読み込み方法を変える
    if upload_files.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        # xlsxファイルの読み込み → データフレームにセット
        df = pd.read_excel(upload_files, sheet_name=0)
    elif upload_files.type == 'text/csv':
        # csvファイルの読み込み → データフレームにセット
        df = pd.read_csv(upload_files)
    # 欠損値を含むレコードを削除
    df.dropna(how='any', inplace=True)

# データフレーム表示ボタン
if st.checkbox('データフレームの表示（クリックで開きます）'):
    st.dataframe(df, width=0)

# 変数選択フォーム
with st.form(key='variable_form'):
    st.subheader("分析に使用する変数の選択")
    # 複数選択
    Variables = st.multiselect('変数（複数選択可）', df.columns.tolist())
    vRange = len(Variables)

    # 確認ボタンの表示
    CHECK_btn = st.form_submit_button('確認')

# 分析前の確認フォーム
with st.form(key='check_form'):
    if CHECK_btn:
        st.subheader('【分析前の確認】')

        n = 0
        for ViewCheck in range(vRange):
            st.write(
                f'● 【'f'{(Variables[n])}】')
            n += 1
        st.write('    '+'これらの変数の出現度数に有意な差が生まれるか検定します。')

    # 分析実行ボタンの表示
    ANALYZE_btn = st.form_submit_button('分析実行')

# 分析結果表示フォーム
with st.form(key='analyze_form'):
    if ANALYZE_btn:
        st.subheader('【分析結果】')

        # chi-square test
        chi2, p, dof, expected = chi2_contingency(df[Variables])

        st.write('Chi-square statistic: ', chi2)
        st.write('p-value: ', p)
        st.write('Degrees of freedom: ', dof)
        st.write('Expected counts: ', expected)

    ANALYZE_btn = st.form_submit_button('OK')

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9',
         'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
