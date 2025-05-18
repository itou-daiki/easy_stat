import streamlit as st
import common

# ページ設定
st.set_page_config(page_title="easyStat", layout="wide")

# カスタムCSSの適用（Google Fonts読み込みとスタイル定義）
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
    /* 全体の背景とフォント設定 */
    body {
        background: linear-gradient(135deg, #e9f0f7, #f7f9fc);
        font-family: 'Roboto', sans-serif;
        color: #202124;
        margin: 0;
        padding: 0;
    }
    /* コンテナのスタイル */
    .container {
        max-width: 1200px;
        margin: 40px auto;
        background-color: #fff;
        border-radius: 12px;
        overflow: hidden;  /* タイトルと中身を一体化 */
    }
    /* タイトル部分 */
    .title {
        background: linear-gradient(135deg, #1a73e8, #4285f4);
        padding: 60px 20px;
        color: #fff;
        text-align: center;
        font-weight: 700;
        font-size: 3.5em;
        margin: 0;  /* 余白をなくす */
        border-radius: 12px 12px 0 0;  /* 上部だけ丸める */
    }
    /* コンテンツ部分 */
    .content {
        padding: 40px;
    }
    /* 更新履歴（スクロール可能に変更） */
    .update-log {
        background-color: #fafafa;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin-bottom: 30px;
        line-height: 1.6;
        max-height: 300px;  /* 高さを300pxに制限 */
        overflow-y: auto;   /* 垂直方向にスクロールを有効に */
    }
    /* リンクセクション */
    .link-section a {
        color: #1a73e8;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s ease;
    }
    .link-section a:hover {
        color: #0c54a0;
    }
    /* 一般テキスト */
    p {
        font-size: 1.15em;
        line-height: 1.8;
    }
    /* レスポンシブ対応 */
    @media (max-width: 768px) {
        .title {
            font-size: 2.5em;
            padding: 40px 10px;
        }
        .content {
            padding: 20px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# コンテナ開始
st.markdown('<div class="container">', unsafe_allow_html=True)

# タイトルをコンテナ内に配置
st.markdown('<div class="title">easyStat（ブラウザ統計）</div>', unsafe_allow_html=True)

# コンテンツ部分開始
st.markdown('<div class="content">', unsafe_allow_html=True)

# ヘッダー表示（common.display_header() の呼び出し）
common.display_header()

# アプリ概要
st.markdown("""
## **概要**
このウェブアプリケーションでは、ブラウザ上で統計分析を行うことができます。iPadなどのデバイスにも対応しています。
""")

# ガイド表示（common.display_guide() の呼び出し）
common.display_guide()

# 機能一覧
st.markdown("実装中の機能は以下の通りです：")
st.markdown("""
- **データクレンジング**
- **探索的データ分析（EDA）**
- **相関分析**
- **カイ２乗分析**
- **ｔ検定（対応なし）**
- **ｔ検定（対応あり）**
- **一要因分散分析（対応なし）**
- **単回帰分析**
- **重回帰分析**
- **因子分析**
- **テキストマイニング**
""")

# 更新履歴セクション
st.header("更新履歴")
st.markdown("""
<div class="update-log">
  <h4><strong>2024/4/18</strong></h4>
  <ul>
    <li>テキストマイニングの共起ネットワーク描画機能を実装しました。</li>
  </ul>
  <h4><strong>2024/2/9</strong></h4>
  <ul>
    <li>二要因分散分析を実装しました。</li>
  </ul>
  <h4><strong>2024/2/7</strong></h4>
  <ul>
    <li>グラフの描画機能を修正しました。</li>
  </ul>
  <h4><strong>2024/12/08</strong></h4>
  <ul>
    <li>ディレクトリを整理しました。</li>
  </ul>
  <h4><strong>2024/11/21</strong></h4>
  <ul>
    <li>単回帰分析の図が正しく描画されるように修正しました。</li>
    <li>テキストマイニングの設計を見直しました。</li>
  </ul>
  <h4><strong>2024/11/13</strong></h4>
  <ul>
    <li>重回帰分析のパス図が正しく描画されるように修正しました。</li>
  </ul>
  <h4><strong>2024/11/04</strong></h4>
  <ul>
    <li>相関分析に散布図行列を表示する機能を追加しました。</li>
  </ul>
  <h4><strong>2024/4/14</strong></h4>
  <ul>
    <li>重回帰分析を実装しました（Provided by Toshiyuki）。</li>
  </ul>
  <h4><strong>2024/3/29</strong></h4>
  <ul>
    <li>単回帰分析を実装しました（Provided by Toshiyuki）。</li>
  </ul>
  <h4><strong>2023/12/7</strong></h4>
  <ul>
    <li>リポジトリを追加しました</li>
    <li>GitHub（<a href="https://easystat-4-education.streamlit.app/" target="_blank">https://easystat-4-education.streamlit.app/</a>）</li>
    <li>Huggingface（<a href="https://huggingface.co/spaces/itou-daiki/easy_stat" target="_blank">https://huggingface.co/spaces/itou-daiki/easy_stat</a>）</li>
    <li>分析に変数選択に制限を設けました</li>
  </ul>
  <h4><strong>2023/10/28</strong></h4>
  <ul>
    <li>一要因分散分析（対応なし）を実装しました。</li>
    <li>グラフタイトルの表示の有無を選択する機能を実装しました。</li>
  </ul>
  <h4><strong>2023/10/26</strong></h4>
  <ul>
    <li>データクレンジングページを実装しました。</li>
    <li>t検定で出力される図に、ブラケットと判定を表示できるようにしました。</li>
  </ul>
  <h4><strong>2023/10/25</strong></h4>
  <ul>
    <li>テキストマイニングを実装しました。</li>
  </ul>
  <h4><strong>2023/10/24</strong></h4>
  <ul>
    <li>探索的データ分析（EDA）を実装しました。</li>
    <li>相関分析を修正しました。</li>
    <li>カイ２乗分析を修正しました。</li>
  </ul>
  <h4><strong>2023/09/01</strong></h4>
  <ul>
    <li>リポジトリを移動しました。</li>
  </ul>
  <h4><strong>2023/08/01</strong></h4>
  <ul>
    <li>簡易データサイエンス機能を実装しました。</li>
    <li>UIとその他の軽微な修正を行いました。</li>
  </ul>
  <h4><strong>2023/03/11</strong></h4>
  <ul>
    <li>相関分析機能を実装しました。</li>
  </ul>
  <h4><strong>2023/03/06</strong></h4>
  <ul>
    <li>ｔ検定（対応あり・なし）を統合しました。</li>
  </ul>
</div>
""", unsafe_allow_html=True)

# リンク・連絡先情報
st.markdown('<div class="link-section">', unsafe_allow_html=True)
common.display_link()
st.markdown('</div>', unsafe_allow_html=True)

# その他の表示
common.display_copyright()
common.display_special_thanks()

# コンテンツ部分終了
st.markdown('</div>', unsafe_allow_html=True) 
st.markdown('</div>', unsafe_allow_html=True) 
