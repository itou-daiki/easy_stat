import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import japanize_matplotlib
import MeCab

# 相対パスでフォントのパスを指定
font_path = "ipaexg.ttf"

# 日本語フォントを設定
mpl.rcParams['font.family'] = 'IPAexGothic' 

# テキストから名詞を取得
def extract_nouns(text):
    mecab = MeCab.Tagger()
    mecab.parse('')  # パース
    node = mecab.parseToNode(text)
    nouns = []
    while node:
        if node.feature.split(",")[0] == "名詞":
            nouns.append(node.surface)
        node = node.next
    return nouns

# テキストから共起ネットワークデータを作成
def create_cooccurrence_data(texts):
    cooccurrence = {}
    for text in texts:
        nouns = extract_nouns(text)
        for i, word1 in enumerate(nouns):
            for j, word2 in enumerate(nouns):
                if i < j:
                    if word1 not in cooccurrence:
                        cooccurrence[word1] = {}
                    if word2 not in cooccurrence[word1]:
                        cooccurrence[word1][word2] = 0
                    cooccurrence[word1][word2] += 1
    return cooccurrence

# StreamlitのUI部分
def main():
    st.title("テキストマイニングWebアプリ")

    uploaded_file = st.file_uploader("ExcelまたはCSVファイルをアップロードしてください", type=["csv", "xlsx"])

    if uploaded_file:
        # ファイルを読み込む
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # ユーザーがテキストデータとして分析するカラムを選択
        text_column = st.selectbox("テキストデータとして分析するカラムを選択してください", df.columns)

        group_column = st.selectbox("群分け変数を選択してください", df.columns)

        for group_name, group_df in df.groupby(group_column):
            st.write(f"### {group_column}：{group_name}の分析")

            # テキストデータの前処理
            cleaned_texts = group_df[text_column].fillna("").astype(str).values
            text = " ".join(cleaned_texts)

            # ワードクラウドの生成
            wordcloud = WordCloud(background_color="white", font_path=font_path, width=800, height=400).generate(text)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)

            # 共起ネットワーク図の生成
            cooccurrence_data = create_cooccurrence_data(cleaned_texts)
            G = nx.Graph()
            for word1, values in cooccurrence_data.items():
                for word2, weight in values.items():
                    G.add_edge(word1, word2, weight=weight)

            MST = nx.minimum_spanning_tree(G, algorithm='kruskal', weight='weight')
            
            pos = nx.spring_layout(MST)
            fig, ax = plt.subplots(figsize=(10, 10))
            nx.draw_networkx(MST, pos, ax=ax, font_family='IPAexGothic')
            ax.axis("off")
            st.pyplot(fig)

            # 品詞ごとの度数をプロット (ここはサンプルとして名詞の度数のみをプロット)
            nouns = []
            for cleaned_text in cleaned_texts:
                nouns.extend(extract_nouns(cleaned_text))
            noun_freq = pd.Series(nouns).value_counts()
            st.bar_chart(noun_freq)

if __name__ == "__main__":
    main()