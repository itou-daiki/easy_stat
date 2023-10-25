import streamlit as st
import pandas as pd
import nlplot
import matplotlib.pyplot as plt
import matplotlib as mpl
import japanize_matplotlib
from PIL import Image


st.set_page_config(page_title="テキストマイニング", layout="wide")

st.title("テキストマイニング")
st.caption("Created by Daiki Ito")
st.write("カテゴリ変数と記述変数からワードクラウドや共起ネットワークを抽出できます")
st.write("")

# 分析のイメージ
image = Image.open('chi_square.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('textmining_demo.xlsx', sheet_name=0)
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
    # 記述変数の抽出
    text_cols = df.select_dtypes(include=['object']).columns.tolist()

    # カテゴリ変数の選択
    st.subheader("カテゴリ変数の選択")
    selected_category = st.selectbox('カテゴリ変数を選択してください', categorical_cols)
    categorical_cols.remove(selected_category)  # 選択済みの変数をリストから削除
    selected_text = st.selectbox('記述変数を選択してください', text_cols)

    # ワードクラウドと共起ネットワークの作成と表示 (全体の分析)
    st.subheader('全体の分析')
    npt = nlplot.NLPlot(df, target_col=selected_text)
        
    # ワードクラウドの作成と表示
    wordcloud = npt.wordcloud(width=800, height=400)
    st.pyplot(wordcloud)
        
    # 共起ネットワークの作成と表示
    network = npt.build_graph(min_edge_frequency=2)
    fig = npt.co_network(network, size='deg')
    st.pyplot(fig)

    # カテゴリ変数で群分け
    st.subheader('カテゴリ別の分析')
    grouped = df.groupby(selected_category)
    for name, group in grouped:
        st.write(f'Category: {name}')
            
        # ワードクラウドと共起ネットワークの作成と表示 (カテゴリ別)
        npt_group = nlplot.NLPlot(group, target_col=selected_text)
            
        # ワードクラウドの作成と表示
        wordcloud_group = npt_group.wordcloud(width=800, height=400)
        st.pyplot(wordcloud_group)
            
        # 共起ネットワークの作成と表示
        network_group = npt_group.build_graph(min_edge_frequency=2)
        fig = npt_group.co_network(network_group, size='deg')
        st.pyplot(fig)
            
else:
    st.error('データフレームがありません。ファイルをアップロードするか、デモデータを使用してください。')






