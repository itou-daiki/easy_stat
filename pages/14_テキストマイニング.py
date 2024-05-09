import streamlit as st
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import networkx as nx
import plotly.express as px
from collections import Counter
import matplotlib.pyplot as plt
import japanize_matplotlib
from PIL import Image
import MeCab
import nlplot

font_path = "ipaexg.ttf"
plt.rcParams['font.family'] = 'IPAexGothic'

st.set_page_config(page_title="テキストマイニング", layout="wide")

st.title("テキストマイニング")
st.caption("Created by Dit-Lab.(Daiki Ito)")
st.write("カテゴリ変数と記述変数からワードクラウドや共起ネットワークを抽出できます")
st.write("")

# 分析のイメージ
image = Image.open('textmining.png')
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
    # カテゴリ変数と記述変数の抽出
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()

    # カテゴリ変数の選択
    st.subheader("カテゴリ変数の選択")
    selected_category = st.selectbox('カテゴリ変数を選択してください', categorical_cols)
    categorical_cols.remove(selected_category)  # 選択済みの変数をリストから削除

    # 記述変数の選択
    st.subheader("記述変数の選択")
    selected_text = st.selectbox('記述変数を選択してください', text_cols)

    # 前処理オプション
    st.subheader("前処理オプション")
    # ストップワードのカスタマイズ
    default_stopwords = ["する", "なる", "ある", "こと", "これ", "それ", "もの", "ため", "ところ", "やる", "れる", "られる","の","を","し","に","です","は","その","ます","が","て","で","と","も"]
    stopwords_input = st.text_input("ストップワードをカンマ区切りで入力 (デフォルトのストップワードに追加されます)", "")
    stopwords_list = default_stopwords + [word.strip() for word in stopwords_input.split(',')] if stopwords_input else default_stopwords

    # MeCabの初期化
    mecab = MeCab.Tagger("-Owakati")

    # nlplotのインスタンス化
    npt = nlplot.NLPlot(df, target_col=selected_text)

    # テキストデータの抽出と前処理
    text_data = df[selected_text].dropna().str.cat(sep=' ')

    # 前処理用の関数
    def preprocess(text):
        nodes = mecab.parseToNode(text)
        words = []
        while nodes:
            features = nodes.feature.split(",")
            if features[0] not in ["助詞"] and nodes.surface not in stopwords_list:
                if features[0] in ["名詞", "動詞", "形容詞", "固有名詞", "感動詞"]:
                    words.append(nodes.surface)
            nodes = nodes.next
        return " ".join(words)

    words = preprocess(text_data)

    st.subheader('全体の分析')

    # ワードクラウドの作成と表示
    st.subheader('【ワードクラウド】')
    max_words_all = st.slider('ワードクラウドの最大単語数', 50, 200, 125, key='max_words_all')
    wordcloud = WordCloud(
        font_path=font_path,
        max_words=max_words_all,
        width=800,
        height=400,
        background_color='white',
        collocations=False,
        stopwords=stopwords_list
    ).generate(words)

    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

    # 共起ネットワークの作成と表示
    st.subheader('【共起ネットワーク】')
    min_edge_frequency_all = st.slider('最小エッジ頻度', 1, 100, 1, key='co_network_all')
    fig_co_network_all = npt.build_graph(df, min_edge_frequency=min_edge_frequency_all)
    st.write(fig_co_network_all)

    # 名詞の度数を棒グラフで表示
    st.subheader('【名詞の出現度数】')
    nouns_frequency = npt.count_nouns(text_data, stopwords=stopwords_list)
    df_nouns = pd.DataFrame(nouns_frequency.items(), columns=['名詞', '度数']).sort_values(by='度数', ascending=False)
    fig_bar_all = px.bar(df_nouns.head(20), x='名詞', y='度数', title="名詞の出現度数")
    st.plotly_chart(fig_bar_all)

    # カテゴリ変数で群分け
    st.subheader('カテゴリ別の分析')
    grouped = df.groupby(selected_category)
    for name, group in grouped:
        st.subheader(f'＜カテゴリ： {name}＞')

        # テキストデータの抽出と前処理 (カテゴリ別)
        text_data_group = group[selected_text].dropna().str.cat(sep=' ')
        words_group = preprocess(text_data_group)

        # ワードクラウドの作成と表示 (カテゴリ別)
        st.subheader('【ワードクラウド】')
        max_words_group = st.slider('ワードクラウドの最大単語数', 50, 200, 125,key=f'max_words_group_{name}')
        wordcloud_group = WordCloud(
            font_path=font_path,
            max_words=max_words_group,
            width=800,
            height=400,
            background_color='white',
            collocations=False,
            stopwords=stopwords_list
        ).generate(words_group)

        fig, ax = plt.subplots()
        ax.imshow(wordcloud_group, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

        # 共起ネットワークの作成と表示 (カテゴリ別)
        st.subheader('【共起ネットワーク】')
        min_edge_frequency_group = st.slider('最小エッジ頻度',1, 100, 100, key=f'co_network_group_{name}')
        fig_co_network_group = npt.build_graph(group, min_edge_frequency=min_edge_frequency_group)
        st.write(fig_co_network_group)

        # 名詞の度数を棒グラフで表示 (カテゴリ別)
        st.subheader('【名詞の出現度数】')
        nouns_frequency_group = npt.count_nouns(text_data_group, stopwords=stopwords_list)
        df_nouns_group = pd.DataFrame(nouns_frequency_group.items(), columns=['名詞', '度数']).sort_values(by='度数', ascending=False)
        fig_bar_group = px.bar(df_nouns_group.head(20), x='名詞', y='度数', title=f"名詞の出現度数　カテゴリ： {name}")
        st.plotly_chart(fig_bar_group)

else:
    st.error('データフレームがありません。ファイルをアップロードするか、デモデータを使用してください。')

# Copyright
st.subheader('© 2022-2024 Dit-Lab.(Daiki Ito). All Rights Reserved.')
st.write("easyStat: Open Source for Ubiquitous Statistics")
st.write("Democratizing data, everywhere.")
st.write("")
st.subheader("In collaboration with our esteemed contributors:")
st.write("・Toshiyuki")
st.write("With heartfelt appreciation for their dedication and support.")