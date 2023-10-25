import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import networkx as nx
import nlplot
import cufflinks as cf
import plotly.express as px
import plotly
from plotly.subplots import make_subplots
from plotly.offline import iplot
from collections import Counter
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
    # デフォルトで最後のカラムを選択する
    default_index = len(text_cols) - 1
    selected_text = st.selectbox('記述変数を選択してください', text_cols, index = default_index)

    st.subheader('全体の分析')

    # MeCabの初期化
    mecab = MeCab.Tagger("-Owakati")
    

    # ワードクラウドと共起ネットワークの作成と表示 (全体の分析)
    npt = nlplot.NLPlot(df, target_col=selected_text)

    # ストップワードの定義 (KH Coderのデフォルトの日本語ストップワードを参考に簡易的に定義)
    STOPWORDS = set(["する", "なる", "ある", "こと", "これ", "それ", "もの", "ため", "ところ", "やる", "れる", "られる","の","を","し","に","です","は","その","ます","が"])
    stopwords_list = list(STOPWORDS) + npt.default_stopwords

    def extract_words(text):
        nodes = mecab.parseToNode(text)
        words = []
        while nodes:
            features = nodes.feature.split(",")
            if features[0] not in ["助詞"] and nodes.surface not in stopwords_list:
                if features[0] in ["名詞", "動詞", "形容詞", "固有名詞", "感動詞"]:
                    words.append(nodes.surface)
            nodes = nodes.next
        return " ".join(words)
    
    # 名詞の度数をカウントする関数
    def count_nouns(text):
        nodes = mecab.parseToNode(text)
        nouns = []
        while nodes:
            features = nodes.feature.split(",")
            if features[0] == "名詞" and nodes.surface not in stopwords_list:
                nouns.append(nodes.surface)
            nodes = nodes.next
        return Counter(nouns)
    
    # テキストデータの抽出と単語の分割
    text_data = df[selected_text].str.cat(sep=' ')
    words = extract_words(text_data) 


    st.subheader('【ワードクラウド】')
    # ワードクラウドのパラメータ
    max_words = st.slider('ワードクラウドの最大単語数', 50, 200, 125, key='max_words_all')

    # ワードクラウドの作成と表示
    wordcloud = WordCloud(
        width=800, height=400, 
        max_words=max_words,
        background_color='white', 
        collocations=False, 
        font_path=font_path,
        min_font_size=4,
        stopwords=stopwords_list
        ).generate(words)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis('off')
    st.pyplot(fig)
        
    # 共起ネットワークの作成と表示
    try:
        st.subheader('【共起ネットワーク】')
        # 共起ネットワークのパラメータ
        min_edge_frequency = st.slider('最小エッジ頻度', 1, 10, 1, key='co_network_all')
        network = npt.build_graph(stopwords=stopwords_list,min_edge_frequency=min_edge_frequency)
        fig = npt.co_network(
            sizing=100,
            node_size='adjacency_frequency', 
            color_palette='hls', 
            width=1100,
            height=700,
            save=True)
        st.plotly_chart(fig)
    except ValueError as e:
        st.error(f'共起ネットワークの作成に失敗しました（アップデート予定）: {str(e)}')
    except Exception as e:
        st.error(f'予期しないエラーが発生しました: {str(e)}')

    # 全体のテキストデータから名詞の度数をカウント
    nouns_frequency = count_nouns(text_data)

    # 名詞の度数をデータフレームに変換
    df_nouns = pd.DataFrame(nouns_frequency.items(), columns=['名詞', '度数']).sort_values(by='度数', ascending=False)

    # 名詞の度数を棒グラフで表示
    fig = px.bar(df_nouns.head(20), x='名詞', y='度数', title="名詞の出現度数")
    st.plotly_chart(fig)


    # カテゴリ変数で群分け
    st.subheader('カテゴリ別の分析')
    grouped = df.groupby(selected_category)
    for name, group in grouped:
        st.write(f'＜カテゴリ： {name}＞')
                        
        # テキストデータの抽出と単語の分割 (カテゴリ別)
        text_data_group = group[selected_text].str.cat(sep=' ')
        words_group = mecab.parse(text_data_group)

        # ワードクラウドと共起ネットワークの作成と表示 (カテゴリ別)
        npt_group = nlplot.NLPlot(group, target_col=selected_text)

        st.subheader('【ワードクラウド】')

        # ワードクラウドのパラメータ
        max_words = st.slider('ワードクラウドの最大単語数', 50, 200, 125,key=f'max_words_group_{name}')

        # ワードクラウドの作成と表示 (カテゴリ別)
        wordcloud_group = WordCloud(
            width=800, height=400, 
            max_words=max_words,
            background_color='white', 
            collocations=False, 
            font_path=font_path,
            min_font_size=4,
            stopwords=stopwords_list
            ).generate(words_group)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud_group, interpolation="bilinear")
        ax.axis('off')
        st.pyplot(fig)

        # カテゴリ別のテキストデータから名詞の度数をカウント
        nouns_frequency_group = count_nouns(text_data_group)

        # 名詞の度数をデータフレームに変換
        df_nouns_group = pd.DataFrame(nouns_frequency_group.items(), columns=['名詞', '度数']).sort_values(by='度数', ascending=False)

        # 名詞の度数を棒グラフで表示
        fig = px.bar(df_nouns_group.head(20), x='名詞', y='度数', title=f"名詞の出現度数　カテゴリ： {name}")
        st.plotly_chart(fig)
            
        # 共起ネットワークの作成と表示
        try:
            st.subheader('【共起ネットワーク】')
            # 共起ネットワークのパラメータ
            min_edge_frequency = st.slider('最小エッジ頻度', 1, 10, 1, key=f'co_network_group_{name}')
            network_group = npt_group.build_graph(stopwords=stopwords_list,min_edge_frequency=min_edge_frequency)
            fig = npt_group.co_network(
                sizing=100,
                node_size='adjacency_frequency', 
                color_palette='hls', 
                width=1100,
                height=700,
                save=True)
            st.plotly_chart(fig)
        except ValueError as e:
            st.error(f'共起ネットワークの作成に失敗しました（アップデート予定）: {str(e)}')
        except Exception as e:
            st.error(f'予期しないエラーが発生しました: {str(e)}')
            
else:
    st.error('データフレームがありません。ファイルをアップロードするか、デモデータを使用してください。')






