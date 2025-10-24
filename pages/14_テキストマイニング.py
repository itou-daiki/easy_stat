import os
from collections import Counter

import japanize_matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import nlplot
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
from janome.tokenizer import Tokenizer
from wordcloud import WordCloud

import common


common.set_font()

# ワードクラウド用のフォントパス設定
# システムフォントを探す
font_candidates = [
    # プロジェクト内のフォント
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ipaexg.ttf'),
    'ipaexg.ttf',
    # システムフォント（Linux/Ubuntu）
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',
    '/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf',
    # デフォルトフォント
    None
]

font_path = None
for candidate in font_candidates:
    if candidate and os.path.exists(candidate):
        # Git LFSポインターファイルでないことを確認
        try:
            with open(candidate, 'rb') as f:
                header = f.read(100)
                if b'git-lfs' not in header:
                    font_path = candidate
                    break
        except:
            pass

if font_path is None:
    # フォントが見つからない場合はWordCloudのデフォルトフォントを使用
    st.warning("日本語フォントが見つかりません。デフォルトフォントを使用します。")

st.set_page_config(page_title="テキストマイニング", layout="wide")

# AI解釈機能の設定
gemini_api_key, enable_ai_interpretation = common.AIStatisticalInterpreter.setup_ai_sidebar()

st.title("テキストマイニング")
common.display_header()
st.write(
    "記述変数からワードクラウドや共起ネットワークを抽出します。"
    "必要に応じてテストデータを補い、必ず共起ネットワークが描画されるようにします。"
)

# 画像の表示
try:
    image = Image.open('images/textmining.png')
    st.image(image)
except FileNotFoundError:
    pass

# ファイルアップロードとデモデータ選択
uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])
use_demo_data = st.checkbox('デモデータを使用')

df = None
if use_demo_data:
    try:
        df = pd.read_excel('datasets/textmining_demo.xlsx', sheet_name=0)
        st.write("デモデータ:")
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
            st.write("アップロードデータ:")
            st.write(df.head())
        except Exception as e:
            st.error(f"ファイル読み込みエラー: {e}")

# データフレームが有効な場合のみ解析開始
if df is not None and not df.empty:
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()

    if not categorical_cols:
        st.error('カテゴリ変数が見つかりません。')
    elif not text_cols:
        st.error('記述変数が見つかりません。')
    else:
        st.subheader("カテゴリ変数の選択")
        selected_category = st.selectbox('カテゴリ変数を選択してください', categorical_cols)
        if selected_category in text_cols:
            text_cols.remove(selected_category)

        default_index = len(text_cols) - 1 if text_cols else 0
        selected_text = st.selectbox('記述変数を選択してください', text_cols, index=default_index)

        st.subheader('全体の分析')
        tokenizer = Tokenizer()

        def extract_words(text):
            if pd.isnull(text):
                return ""
            tokens = tokenizer.tokenize(text)
            return ' '.join(
                token.base_form
                for token in tokens
                if token.part_of_speech.split(',')[0] in ["名詞", "動詞", "形容詞", "副詞"]
            )

        df['tokenized_text'] = df[selected_text].apply(extract_words)
        total_tokens = df['tokenized_text'].str.split().apply(len).sum()
        st.write(f"トークン化後の総単語数: {total_tokens}")

        # 共起が発生しない場合のテスト行追加
        if not df['tokenized_text'].str.strip().any():
            df = pd.concat([
                df,
                pd.DataFrame({
                    selected_category: ["テストカテゴリ"],
                    selected_text: ["テスト テスト テキスト テキスト"]
                })
            ], ignore_index=True)
            df['tokenized_text'] = df[selected_text].apply(extract_words)

        # NLPlot 初期化
        npt = nlplot.NLPlot(df, target_col='tokenized_text')
        stopwords_list = npt.get_stopword()
        words = ' '.join(df['tokenized_text'])

        # ワードクラウド
        st.subheader('【ワードクラウド】')
        max_words = st.slider(
            '最大単語数', 10, max(len(set(words.split())), 10), 50
        )
        if words:
            wc = WordCloud(
                width=800, height=400, max_words=max_words,
                background_color='white', font_path=font_path,
                collocations=False, stopwords=set(stopwords_list)
            ).generate(words)
            fig_wc, ax_wc = plt.subplots()
            ax_wc.imshow(wc, interpolation='bilinear')
            ax_wc.axis('off')
            st.pyplot(fig_wc)

        # 全体の共起ネットワーク
        st.subheader('【共起ネットワーク（全体）】')
        npt.build_graph(stopwords=stopwords_list, min_edge_frequency=1)
        fig_net = npt.co_network(
            title='全体の共起ネットワーク', sizing=100,
            node_size='adjacency_frequency', color_palette='hls',
            width=1000, height=600, save=False
        )
        if fig_net is not None:
            st.plotly_chart(fig_net, use_container_width=True)
        else:
            # フォールバック: KH Coder デフォルト Top 60
            edges = sorted(
                npt.graph.edges(data=True),
                key=lambda x: x[2].get('weight',1), reverse=True
            )[:60]
            subG = nx.Graph()
            subG.add_nodes_from(npt.graph.nodes(data=True))
            subG.add_edges_from([(u,v) for u,v,_ in edges])
            pos = nx.kamada_kawai_layout(subG)
            fig_nx, ax_nx = plt.subplots(figsize=(8,6))
            nx.draw(subG, pos, with_labels=True,
                    font_family='IPAexGothic', node_size=300,
                    edge_color='gray')
            ax_nx.set_title('全体の共起ネットワーク (Top60)')
            ax_nx.axis('off')
            st.pyplot(fig_nx)

        # 単語度数バー
        freq = Counter(words.split())
        df_freq = pd.DataFrame(
            freq.items(), columns=['単語','度数']
        ).sort_values(by='度数', ascending=False)
        if not df_freq.empty:
            fig_bar = px.bar(
                df_freq.head(20), x='単語', y='度数',
                title='出現度数トップ20'
            )
            st.plotly_chart(fig_bar)

        # --- AI解釈機能 ---
        if enable_ai_interpretation and gemini_api_key:
            try:
                # top_wordsをリスト形式で取得
                top_words = [(row["単語"], row["度数"]) for _, row in df_freq.head(30).iterrows()]
                n_documents = len(df)
                n_unique_words = len(freq)
                
                text_results = {
                    'top_words': top_words,
                    'n_documents': n_documents,
                    'n_unique_words': n_unique_words
                }
                
                common.AIStatisticalInterpreter.display_ai_interpretation(
                    api_key=gemini_api_key,
                    enabled=enable_ai_interpretation,
                    results=text_results,
                    analysis_type='text_mining',
                    key_prefix='text_mining'
                )
            except Exception as e:
                st.warning(f"AI解釈の生成中にエラーが発生しました: {str(e)}")

        # カテゴリ별分析と描画
        for cat, grp in df.groupby(selected_category):
            st.subheader(f'＜カテゴリ：{cat}＞')
            grp['tokenized_text'] = grp[selected_text].apply(extract_words)
            words_cat = ' '.join(grp['tokenized_text'])

            # カテゴリ별ワードクラウド
            if words_cat:
                wc_cat = WordCloud(
                    width=600, height=300, max_words=50,
                    background_color='white', font_path=font_path,
                    collocations=False, stopwords=set(stopwords_list)
                ).generate(words_cat)
                fig_c, ax_c = plt.subplots()
                ax_c.imshow(wc_cat, interpolation='bilinear')
                ax_c.axis('off')
                st.pyplot(fig_c)

            # カテゴリ별共起ネットワーク
            npt_cat = nlplot.NLPlot(grp, target_col='tokenized_text')
            npt_cat.build_graph(stopwords=stopwords_list, min_edge_frequency=1)
            fig_cat = npt_cat.co_network(
                title=f'{cat}の共起ネットワーク', sizing=80,
                node_size='adjacency_frequency', color_palette='hls',
                width=800, height=500, save=False
            )
            if fig_cat is not None:
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                edges_cat = sorted(
                    npt_cat.graph.edges(data=True),
                    key=lambda x: x[2].get('weight',1), reverse=True
                )[:60]
                subG_cat = nx.Graph()
                subG_cat.add_nodes_from(npt_cat.graph.nodes(data=True))
                subG_cat.add_edges_from([(u,v) for u,v,_ in edges_cat])
                pos_cat = nx.kamada_kawai_layout(subG_cat)
                fig_nx2, ax_nx2 = plt.subplots(figsize=(6,5))
                nx.draw(subG_cat, pos_cat, with_labels=True,
                        font_family='IPAexGothic', node_size=300)
                ax_nx2.set_title(f'{cat}の共起ネットワーク (Top60)')
                ax_nx2.axis('off')
                st.pyplot(fig_nx2)

# フッター
common.display_copyright()
common.display_special_thanks()
