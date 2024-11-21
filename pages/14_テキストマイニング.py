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
from janome.tokenizer import Tokenizer
import nlplot

font_path = "ipaexg.ttf"
plt.rcParams['font.family'] = 'IPAexGothic'

st.set_page_config(page_title="テキストマイニング", layout="wide")

st.title("テキストマイニング")
st.caption("Created by Dit-Lab.(Daiki Ito)")
st.write("カテゴリ変数と記述変数からワードクラウドや共起ネットワークを抽出できます")
st.write("")

# 分析のイメージ
try:
    image = Image.open('textmining.png')
    st.image(image)
except FileNotFoundError:
    st.warning("画像ファイル 'textmining.png' が見つかりません。")

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    try:
        df = pd.read_excel('textmining_demo.xlsx', sheet_name=0)
        st.write("デモデータの先頭5行:")
        st.write(df.head())
    except FileNotFoundError:
        st.error("デモデータファイル 'textmining_demo.xlsx' が見つかりません。")
else:
    if uploaded_file is not None:
        try:
            if uploaded_file.type == 'text/csv':
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.write("アップロードされたデータの先頭5行:")
            st.write(df.head())
        except Exception as e:
            st.error(f"ファイルの読み込み中にエラーが発生しました: {e}")

if df is not None:
    # カテゴリ変数の抽出
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    # 記述変数の抽出
    text_cols = df.select_dtypes(include=['object']).columns.tolist()

    if not categorical_cols:
        st.error('カテゴリ変数が見つかりません。適切なデータを使用してください。')
    elif not text_cols:
        st.error('記述変数が見つかりません。適切なデータを使用してください。')
    else:
        # カテゴリ変数の選択
        st.subheader("カテゴリ変数の選択")
        selected_category = st.selectbox('カテゴリ変数を選択してください', categorical_cols)
        # 選択済みの変数をリストから削除
        text_cols.remove(selected_category)
        # デフォルトで最後のカラムを選択する
        default_index = len(text_cols) - 1 if len(text_cols) > 0 else 0
        selected_text = st.selectbox('記述変数を選択してください', text_cols, index=default_index)

        st.subheader('全体の分析')

        # Janomeの初期化
        tokenizer = Tokenizer()

        def extract_words(text):
            if pd.isnull(text):
                return ""
            tokens = tokenizer.tokenize(text)
            words = []
            for token in tokens:
                part_of_speech = token.part_of_speech.split(',')[0]
                if part_of_speech in ["名詞", "動詞", "形容詞", "副詞"]:
                    base_form = token.base_form
                    words.append(base_form)
            return ' '.join(words)

        # テキストデータをトークン化して新しい列に保存
        df['tokenized_text'] = df[selected_text].apply(extract_words)

        # トークン化後の単語数を表示
        total_tokens = df['tokenized_text'].str.split().apply(len).sum()
        st.write(f"トークン化後の総単語数: {total_tokens}")

        # nptの初期化
        npt = nlplot.NLPlot(df, target_col='tokenized_text')

        # ストップワードをライブラリから取得
        stopwords_list = npt.get_stopword()

        # テキストデータの抽出
        text_data = ' '.join(df['tokenized_text'])
        words = text_data

        st.subheader('【ワードクラウド】')
        # ワードクラウドのパラメータ
        unique_words = set(words.split())
        max_words_default = min(len(unique_words), 125)
        max_words = st.slider('ワードクラウドの最大単語数', 10, len(unique_words), max_words_default, key='max_words_all')

        if words:
            # ワードクラウドの作成と表示
            wordcloud = WordCloud(
                width=800, height=400,
                max_words=max_words,
                background_color='white',
                collocations=False,
                font_path=font_path,
                min_font_size=4,
                stopwords=set(stopwords_list)
            ).generate(words)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.warning("トークン化後のテキストデータが空です。ストップワードの設定を見直してください。")

        # 共起ネットワークの構築
        npt.build_graph(stopwords=stopwords_list, min_edge_frequency=1)
        if not hasattr(npt, 'edge_df') or npt.edge_df.empty:
            st.warning("共起ネットワークのエッジリストが空です。ストップワードを調整するか、データを確認してください。")
        else:
            max_edge_frequency = int(npt.edge_df['count'].max())

            # 共起ネットワークのパラメータ
            min_edge_frequency_default = max(1, int(max_edge_frequency * 0.1))

            st.subheader('【共起ネットワーク】')
            min_edge_frequency = st.slider('最小エッジ頻度', 1, max_edge_frequency, min_edge_frequency_default, key='co_network_all')

            # 再度グラフを構築（最小エッジ頻度を適用）
            npt.build_graph(stopwords=stopwords_list, min_edge_frequency=min_edge_frequency)

            # グラフが構築されているか確認
            if hasattr(npt, 'graph') and isinstance(npt.graph, nx.Graph):
                num_edges = npt.graph.number_of_edges()
                num_nodes = npt.graph.number_of_nodes()
                st.write(f"共起ネットワークのノード数: {num_nodes}, エッジ数: {num_edges}")

                if num_edges > 0:
                    fig_co_network_all = npt.co_network(
                        title='共起ネットワーク（全体）',
                        sizing=100,
                        node_size='adjacency_frequency',
                        cmap='hls',  # 修正箇所
                        width=1100,
                        height=700,
                        save=False
                    )
                    st.plotly_chart(fig_co_network_all)
                else:
                    st.warning("共起ネットワークを生成できませんでした。ストップワードを調整するか、データを確認してください。")
            else:
                st.warning("共起ネットワークのグラフが構築されていません。ストップワードを調整するか、データを確認してください。")

        # 単語の度数をカウント
        if words:
            words_list = words.split()
            words_frequency = Counter(words_list)

            # 単語の度数をデータフレームに変換
            df_words = pd.DataFrame(words_frequency.items(), columns=['単語', '度数']).sort_values(by='度数', ascending=False)

            # 単語の度数を棒グラフで表示
            if not df_words.empty:
                fig = px.bar(df_words.head(20), x='単語', y='度数', title="単語の出現度数")
                st.plotly_chart(fig)
            else:
                st.warning("単語のカウントに失敗しました。トークン化後のテキストデータを確認してください。")
        else:
            st.warning("トークン化後のテキストデータが空です。単語のカウントができません。")

        # カテゴリ変数で群分け
        st.subheader('カテゴリ別の分析')
        grouped = df.groupby(selected_category)
        for name, group in grouped:
            st.subheader(f'＜カテゴリ： {name}＞')

            grouped_df = group[[selected_category, selected_text, 'tokenized_text']]
            # テキストデータの抽出 (カテゴリ別)
            text_data_group = ' '.join(grouped_df['tokenized_text'])
            words_group = text_data_group

            # トークン化後の単語数を表示
            tokens_group = grouped_df['tokenized_text'].str.split().apply(len).sum()
            st.write(f"カテゴリ '{name}' のトークン化後の総単語数: {tokens_group}")

            npt_group = nlplot.NLPlot(grouped_df, target_col='tokenized_text')

            st.subheader('【ワードクラウド】')

            # ワードクラウドのパラメータ
            unique_words_group = set(words_group.split())
            max_words_default_group = min(len(unique_words_group), 125)
            max_words_group = st.slider('ワードクラウドの最大単語数', 10, len(unique_words_group), max_words_default_group, key=f'max_words_group_{name}')

            if words_group:
                # ワードクラウドの作成と表示 (カテゴリ別)
                wordcloud_group = WordCloud(
                    width=800, height=400,
                    max_words=max_words_group,
                    background_color='white',
                    collocations=False,
                    font_path=font_path,
                    min_font_size=4,
                    stopwords=set(stopwords_list)
                ).generate(words_group)
                fig, ax = plt.subplots()
                ax.imshow(wordcloud_group, interpolation="bilinear")
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.warning(f"カテゴリ '{name}' のトークン化後のテキストデータが空です。ストップワードの設定を見直してください。")

            # 単語の度数をカウント
            if words_group:
                words_list_group = words_group.split()
                words_frequency_group = Counter(words_list_group)

                # 単語の度数をデータフレームに変換
                df_words_group = pd.DataFrame(words_frequency_group.items(), columns=['単語', '度数']).sort_values(by='度数', ascending=False)

                # 単語の度数を棒グラフで表示
                if not df_words_group.empty:
                    fig = px.bar(df_words_group.head(20), x='単語', y='度数', title=f"単語の出現度数　カテゴリ： {name}")
                    st.plotly_chart(fig)
                else:
                    st.warning(f"カテゴリ '{name}' の単語のカウントに失敗しました。トークン化後のテキストデータを確認してください。")
            else:
                st.warning(f"カテゴリ '{name}' のトークン化後のテキストデータが空です。単語のカウントができません。")

            # 共起ネットワークの構築
            npt_group.build_graph(stopwords=stopwords_list, min_edge_frequency=1)
            if not hasattr(npt_group, 'edge_df') or npt_group.edge_df.empty:
                st.warning(f"カテゴリ '{name}' の共起ネットワークのエッジリストが空です。ストップワードを調整するか、データを確認してください。")
            else:
                max_edge_frequency_group = int(npt_group.edge_df['count'].max())

                # 共起ネットワークのパラメータ
                min_edge_frequency_default_group = max(1, int(max_edge_frequency_group * 0.1))
                min_edge_frequency_group = st.slider('最小エッジ頻度', 1, max_edge_frequency_group, min_edge_frequency_default_group, key=f'co_network_group_{name}')

                # 再度グラフを構築（最小エッジ頻度を適用）
                npt_group.build_graph(stopwords=stopwords_list, min_edge_frequency=min_edge_frequency_group)

                # グラフが構築されているか確認
                if hasattr(npt_group, 'graph') and isinstance(npt_group.graph, nx.Graph):
                    num_edges_group = npt_group.graph.number_of_edges()
                    num_nodes_group = npt_group.graph.number_of_nodes()
                    st.write(f"カテゴリ '{name}' の共起ネットワークのノード数: {num_nodes_group}, エッジ数: {num_edges_group}")

                    if num_edges_group > 0:
                        fig_co_network_grouped = npt_group.co_network(
                            title=f'共起ネットワーク（カテゴリ：{name}）',
                            sizing=100,
                            node_size='adjacency_frequency',
                            cmap='hls',  # 修正箇所
                            width=1100,
                            height=700,
                            save=False
                        )
                        st.plotly_chart(fig_co_network_grouped)
                    else:
                        st.warning(f"カテゴリ '{name}' の共起ネットワークを生成できませんでした。ストップワードを調整するか、データを確認してください。")
                else:
                    st.warning(f"カテゴリ '{name}' の共起ネットワークのグラフが構築されていません。ストップワードを調整するか、データを確認してください。")

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
