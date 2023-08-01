import streamlit as st

st.set_page_config(page_title="ブラウザ統計", layout="wide")

# App title and creator
st.title("ブラウザ統計")
st.caption("Created by Daiki Ito")

# Introduction
st.markdown("""
このウェブアプリケーションでは、ブラウザ上で統計分析を行うことができます。iPadなどのデバイスでも対応しています。""")
st.markdown("""具体的な機能は以下の通りです：""")

# List of implemented tests
st.markdown("""
- 簡易データサイエンス
- 相関分析
- ｔ検定（対応なし）
- ｔ検定（対応あり）
""")

# Updates and history
st.header("更新履歴")

st.markdown("""
#### 2023/08/01
- 簡易データサイエンス機能を実装しました
- UIとその他の軽微な修正を行いました

#### 2023/03/11
- 相関分析機能を実装しました

#### 2023/03/06
- ｔ検定（対応あり・なし）を統合しました
""")

# Contact and repository info
st.header("リンク")
st.markdown("""
- [フィードバックはこちらまで](https://forms.gle/G5sMYm7dNpz2FQtU9)
""")

# Copyright
st.markdown('© 2022-2023 Daiki Ito. All Rights Reserved.')
