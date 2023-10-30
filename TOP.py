import streamlit as st

st.set_page_config(page_title="ブラウザ統計", layout="wide")

# App title and creator
st.title("easyStat（ブラウザ統計）")
st.caption("Created by Daiki Ito")

# Introduction
st.markdown("""
## **概要**
このウェブアプリケーションでは、ブラウザ上で統計分析を行うことができます。iPadなどのデバイスでも対応しています。""")

st.markdown("""
- [**情報探究ステップアップガイド**](https://thorn-rumba-3a4.notion.site/612d9665350544aa97a2a8514a03c77c?v=0266abc5c1384b44a757b9044469d6bd&pvs=4)""")

st.markdown("""実装中の機能は以下の通りです：""")
# List of implemented tests
st.markdown("""- [**データクレンジング**](https://easystat-4-education.streamlit.app/データクレンジング)""")
st.markdown("""- [**探索的データ分析（EDA）**](https://easystat-4-education.streamlit.app/探索的データ分析（EDA）)""")
st.markdown("""- [**相関分析**](https://easystat-4-education.streamlit.app/相関分析)""")
st.markdown("""- [**カイ２乗分析**](https://easystat-4-education.streamlit.app/カイ２乗検定)""")
st.markdown("""- [**ｔ検定（対応なし）**](https://easystat-4-education.streamlit.app/t検定（対応なし）)""")
st.markdown("""- [**ｔ検定（対応あり）**](https://easystat-4-education.streamlit.app/t検定（対応あり）)""")
st.markdown("""- [**一要因分散分析（対応なし）**](https://easystat-4-education.streamlit.app/一要因分散分析（対応なし）)""")
st.markdown("""- [**テキストマイニング**](https://easystat-4-education.streamlit.app/テキストマイニング)""")

# Updates and history
st.header("更新履歴")

st.markdown("""
#### **2023/10/28**
- 一要因分散分析（対応なし）を実装しました
- グラフタイトルの表示の有無を選択する機能を実装しました

#### **2023/10/26**
- データクレンジングページを実装しました
- t検定で出力される図に、ブラケットと判定を表示できるようにしました。

#### **2023/10/25**
- テキストマイニングを実装しました
            
#### **2023/10/24**
- 探索的データ分析（EDA）を実装しました
- 相関分析を修正しました
- カイ２乗分析を修正しました
                        
#### **2023/09/01**
- リポジトリを移動しました。
- 旧URL（https://dddd-onigiri-easy-stat-top-532p3c.streamlit.app/）            

#### **2023/08/01**
- 簡易データサイエンス機能を実装しました
- UIとその他の軽微な修正を行いました

#### **2023/03/11**
- 相関分析機能を実装しました

#### **2023/03/06**
- ｔ検定（対応あり・なし）を統合しました
""")

# Contact and repository info
st.header("リンク")
st.markdown("""
- [**AutoML DataScience**](https://huggingface.co/spaces/itou-daiki/pycaret_datascience_streamlit)
- [**音のデータサイエンス**](https://audiovisualizationanalysis-bpeekdjwymuf6nkqcb4cqy.streamlit.app/)
- [**フィードバックはこちらまで**](https://forms.gle/G5sMYm7dNpz2FQtU9)
- [**ソースコードはこちら（GitHub）**](https://github.com/itou-daiki/easy_stat)
""")

# Copyright
st.markdown('© 2022-2023 Daiki Ito. All Rights Reserved.')
