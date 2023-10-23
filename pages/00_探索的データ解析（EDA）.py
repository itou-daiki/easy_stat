import streamlit as st
import pandas as pd
import dtale
import matplotlib.pyplot as plt
import japanize_matplotlib
import streamlit.components.v1 as components

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
if use_demo_data:
    df = pd.read_excel('eda_demo.xlsx', sheet_name=0)
else:
    if uploaded_file is not None:
        if uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

st.write(df.head())

# データフレームが存在する場合にD-taleで表示
if 'df' in locals() or 'df' in globals():
    try:
        # D-taleインスタンスの作成
        d = dtale.show(df)

        # D-taleアプリをiframe内に埋め込む
        components.iframe(d._main_url, width=1000, height=500)
        
        # D-taleアプリをiframe内に埋め込む
        iframe_code = f'''
            <iframe src="{d._main_url}" width="100%" height="500px" style="border:none;">
            </iframe>
        '''
        st.markdown(iframe_code, unsafe_allow_html=True)

        st.write(f'D-Tale URL: {d._main_url}')

    except Exception as e:
        st.write(f'エラー: {e}')

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')