import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import networkx as nx
import nlplot
import matplotlib.pyplot as plt
import matplotlib as mpl
import japanize_matplotlib
from PIL import Image
import MeCab

font_path = "ipaexg.ttf"

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
        
    # ストップワードの定義 (KH Coderのデフォルトの日本語ストップワードを参考に簡易的に定義)
    STOPWORDS = set(["する", "なる", "ある", "こと", "これ", "それ", "もの", "ため", "ところ", "やる", "れる", "られる",])

    # MeCabの初期化
    mecab = MeCab.Tagger("-Owakati")

    def extract_words(text):
        nodes = mecab.parseToNode(text)
        words = []
        while nodes:
            features = nodes.feature.split(",")
            if len(nodes.surface) > 1 and nodes.surface not in STOPWORDS:
                if features[0] in ["名詞", "動詞", "形容詞", "固有名詞", "感動詞"]:
                    words.append(nodes.surface)
            nodes = nodes.next
        return " ".join(words)


    # テキストデータの抽出と単語の分割
    text_data = df[selected_text].str.cat(sep=' ')
    words = extract_words(text_data) 

    # ワードクラウドの作成と表示
    wordcloud = WordCloud(
        width=800, height=400, 
        background_color='white', 
        collocations=False, 
        font_path=font_path,
        min_font_size=4
        ).generate(words)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis('off')
    st.pyplot(fig)
        
    # 共起ネットワークの作成と表示
    try:
        network = npt.build_graph(min_edge_frequency=2)
        fig = npt.co_network(network, size='deg')
        st.pyplot(plt.gcf())
    except ValueError as e:
        st.error(f'共起ネットワークの作成に失敗しました: {str(e)}')

    # カテゴリ変数で群分け
    st.subheader('カテゴリ別の分析')
    grouped = df.groupby(selected_category)
    for name, group in grouped:
        st.write(f'＜カテゴリ： {name}＞')
            
        # ワードクラウドと共起ネットワークの作成と表示 (カテゴリ別)
        npt_group = nlplot.NLPlot(group, target_col=selected_text)
            
        # テキストデータの抽出と単語の分割 (カテゴリ別)
        text_data_group = group[selected_text].str.cat(sep=' ')
        words_group = mecab.parse(text_data_group)

        # ワードクラウドの作成と表示 (カテゴリ別)
        wordcloud_group = WordCloud(
            width=800, height=400, 
            background_color='white', 
            collocations=False, 
            font_path=font_path,
            min_font_size=4
            ).generate(words_group)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud_group, interpolation="bilinear")
        ax.axis('off')
        st.pyplot(fig)
            
        # 共起ネットワークの作成と表示
        try:
            network_group = npt_group.build_graph(min_edge_frequency=2)
            fig = npt_group.co_network(network_group, size='deg')
            st.pyplot(plt.gcf())
        except ValueError as e:
            st.error(f'共起ネットワークの作成に失敗しました: {str(e)}')
            
else:
    st.error('データフレームがありません。ファイルをアップロードするか、デモデータを使用してください。')






