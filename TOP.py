import streamlit as st

st.set_page_config(page_title="easyStat", layout="wide")

# App title and creator
st.title("easyStat（ブラウザ統計）")
st.caption("Created by Dit-Lab.(Daiki Ito)")

# Introduction
st.markdown("""
## **概要**
このウェブアプリケーションでは、ブラウザ上で統計分析を行うことができます。iPadなどのデバイスでも対応しています。""")

st.markdown("""
- [**情報探究ステップアップガイド**](https://dit-lab.notion.site/612d9665350544aa97a2a8514a03c77c?v=85ad37a3275b4717a0033516b9cfd9cc)""")

st.markdown("""実装中の機能は以下の通りです：""")
# List of implemented tests
st.markdown("""- [**データクレンジング**]""")
st.markdown("""- [**探索的データ分析（EDA）**]""")
st.markdown("""- [**相関分析**]""")
st.markdown("""- [**カイ２乗分析**]""")
st.markdown("""- [**ｔ検定（対応なし）**]""")
st.markdown("""- [**ｔ検定（対応あり）**]""")
st.markdown("""- [**一要因分散分析（対応なし）**]""")
st.markdown("""- [**単回帰分析**]""")
st.markdown("""- [**テキストマイニング**]""")

# Updates and history
st.header("更新履歴")

st.markdown("""

#### **2024/3/29**
- 単回帰分析を実装しました（Provided by Toshiyuki）

#### **2023/12/7**
- リポジトリを追加しました
- GitHub（https://easystat-4-education.streamlit.app/）
- Huggingface（https://huggingface.co/spaces/itou-daiki/easy_stat）      
- 分析に変数選択に制限を設けました            
            
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
st.markdown('© 2022-2024 Dit-Lab.(Daiki Ito). All Rights Reserved.')
st.markdown("""
In collaboration with our esteemed contributors:
- Toshiyuki
With heartfelt appreciation for their dedication and support.
""")
st.subheader("easyStat: Open Source for Ubiquitous Statistics")
st.write("Democratizing data, everywhere.")


