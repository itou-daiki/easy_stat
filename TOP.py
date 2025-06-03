import streamlit as st

import common


# ページ設定
st.set_page_config(page_title='easyStat', layout='wide')

# カスタムCSSの適用（モダンなデザイン）
st.html("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
    /* CSS変数でテーマカラーを定義 */
    :root {
        --primary-color: #6366f1;
        --primary-dark: #4f46e5;
        --secondary-color: #8b5cf6;
        --accent-color: #ec4899;
        --background: #f8fafc;
        --surface: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* 全体の背景とフォント設定 */
    .stApp {
        background: var(--background);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* メインコンテナ */
    .main-container {
        max-width: 1280px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* ヒーローセクション */
    .hero-section {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 24px;
        padding: 4rem 2rem;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.3; }
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        font-weight: 300;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* セクションスタイル */
    .section {
        background: var(--surface);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .section:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .section-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-icon {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.25rem;
    }
    
    /* 機能カードグリッド */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .feature-card {
        background: var(--surface);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-color);
    }
    
    .feature-card:hover::before {
        transform: translateX(0);
    }
    
    .feature-card-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .feature-card-icon {
        color: var(--primary-color);
        font-size: 1.25rem;
    }
    
    .feature-card-description {
        font-size: 0.875rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    /* 更新履歴のスタイル */
    .update-timeline {
        position: relative;
        padding-left: 2rem;
        max-height: 400px;
        overflow-y: auto;
        scrollbar-width: thin;
        scrollbar-color: var(--primary-color) var(--border-color);
    }
    
    .update-timeline::-webkit-scrollbar {
        width: 6px;
    }
    
    .update-timeline::-webkit-scrollbar-track {
        background: var(--border-color);
        border-radius: 3px;
    }
    
    .update-timeline::-webkit-scrollbar-thumb {
        background: var(--primary-color);
        border-radius: 3px;
    }
    
    .update-timeline::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 2px;
        background: var(--border-color);
    }
    
    .update-item {
        position: relative;
        padding-bottom: 2rem;
    }
    
    .update-item::before {
        content: '';
        position: absolute;
        left: -2rem;
        top: 0.5rem;
        width: 12px;
        height: 12px;
        background: var(--primary-color);
        border-radius: 50%;
        box-shadow: 0 0 0 4px var(--surface), 0 0 0 6px var(--border-color);
    }
    
    .update-date {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    
    .update-content {
        font-size: 0.875rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    .update-content ul {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    .update-content li {
        margin-bottom: 0.25rem;
    }
    
    /* リンクスタイル */
    .link-button {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
    }
    
    .link-button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        color: white;
        text-decoration: none;
    }
    
    /* バッジスタイル */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        background: rgba(99, 102, 241, 0.1);
        color: var(--primary-color);
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .badge-new {
        background: rgba(236, 72, 153, 0.1);
        color: var(--accent-color);
    }
    
    /* レスポンシブ対応 */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .main-container {
            padding: 1rem;
        }
        
        .section {
            padding: 1.5rem;
        }
        
        .feature-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* アニメーション */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out forwards;
    }
    </style>
""")

# メインコンテナ
st.html('<div class="main-container">')

# ヒーローセクション
st.html("""
<div class="hero-section fade-in">
    <h1 class="hero-title">easyStat</h1>
    <p class="hero-subtitle">ブラウザで簡単に統計分析を実行</p>
</div>
""")

# ヘッダー表示
common.display_header()

# 概要セクション
st.html("""
<div class="section fade-in">
    <h2 class="section-title">
        <div class="section-icon"><i class="fas fa-info-circle"></i></div>
        概要
    </h2>
    <p style="color: var(--text-secondary); line-height: 1.8;">
        easyStatは、ブラウザ上で手軽に統計分析を行えるウェブアプリケーションです。
        データサイエンスの初心者から上級者まで、幅広いユーザーに対応しています。
    </p>
</div>
""")

# ガイド表示
common.display_guide()

# 機能一覧セクション
st.html("""
<div class="section fade-in">
    <h2 class="section-title">
        <div class="section-icon"><i class="fas fa-chart-line"></i></div>
        利用可能な分析機能
    </h2>
    <div class="feature-grid">
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-broom feature-card-icon"></i>
                データクレンジング
            </h3>
            <p class="feature-card-description">データの前処理と品質向上</p>
        </div>
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-search feature-card-icon"></i>
                探索的データ分析（EDA）
            </h3>
            <p class="feature-card-description">データの特徴と傾向を視覚的に把握</p>
        </div>
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-project-diagram feature-card-icon"></i>
                相関分析
            </h3>
            <p class="feature-card-description">変数間の関係性を分析</p>
        </div>
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-table feature-card-icon"></i>
                カイ２乗検定
            </h3>
            <p class="feature-card-description">カテゴリカルデータの独立性検定</p>
        </div>
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-vial feature-card-icon"></i>
                t検定（対応なし）
            </h3>
            <p class="feature-card-description">2群間の平均値の差を検定</p>
        </div>
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-vials feature-card-icon"></i>
                t検定（対応あり）
            </h3>
            <p class="feature-card-description">対応のあるデータの平均値差を検定</p>
        </div>
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-chart-bar feature-card-icon"></i>
                一要因分散分析
                <span class="badge">対応あり/なし</span>
            </h3>
            <p class="feature-card-description">3群以上の平均値の差を検定</p>
        </div>
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-chart-area feature-card-icon"></i>
                二要因分散分析
                <span class="badge-new">New</span>
            </h3>
            <p class="feature-card-description">2つの要因の効果を同時に分析</p>
        </div>
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-chart-line feature-card-icon"></i>
                単回帰分析
            </h3>
            <p class="feature-card-description">1つの説明変数で予測モデルを構築</p>
        </div>
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-layer-group feature-card-icon"></i>
                重回帰分析
            </h3>
            <p class="feature-card-description">複数の説明変数で予測モデルを構築</p>
        </div>
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-sitemap feature-card-icon"></i>
                因子分析
            </h3>
            <p class="feature-card-description">潜在的な因子構造を探索</p>
        </div>
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-compress-arrows-alt feature-card-icon"></i>
                主成分分析
            </h3>
            <p class="feature-card-description">データの次元削減と可視化</p>
        </div>
        <div class="feature-card">
            <h3 class="feature-card-title">
                <i class="fas fa-file-alt feature-card-icon"></i>
                テキストマイニング
                <span class="badge-new">Updated</span>
            </h3>
            <p class="feature-card-description">テキストデータの分析と可視化</p>
        </div>
    </div>
</div>
""")

# 更新履歴セクション
st.html("""
<div class="section fade-in">
    <h2 class="section-title">
        <div class="section-icon"><i class="fas fa-history"></i></div>
        更新履歴
    </h2>
    <div class="update-timeline">
        <div class="update-item">
            <div class="update-date">2025/6/4</div>
            <div class="update-content">
                <ul>
                    <li>トップページのデザインを刷新しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2025/4/18</div>
            <div class="update-content">
                <ul>
                    <li>テキストマイニングの共起ネットワーク描画機能を実装しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2025/2/9</div>
            <div class="update-content">
                <ul>
                    <li>二要因分散分析を実装しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2025/2/7</div>
            <div class="update-content">
                <ul>
                    <li>グラフの描画機能を修正しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2024/12/08</div>
            <div class="update-content">
                <ul>
                    <li>ディレクトリを整理しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2024/11/21</div>
            <div class="update-content">
                <ul>
                    <li>単回帰分析の図が正しく描画されるように修正しました。</li>
                    <li>テキストマイニングの設計を見直しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2024/11/13</div>
            <div class="update-content">
                <ul>
                    <li>重回帰分析のパス図が正しく描画されるように修正しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2024/11/04</div>
            <div class="update-content">
                <ul>
                    <li>相関分析に散布図行列を表示する機能を追加しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2024/4/14</div>
            <div class="update-content">
                <ul>
                    <li>重回帰分析を実装しました（Provided by Toshiyuki）。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2024/3/29</div>
            <div class="update-content">
                <ul>
                    <li>単回帰分析を実装しました（Provided by Toshiyuki）。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2023/12/7</div>
            <div class="update-content">
                <ul>
                    <li>リポジトリを追加しました</li>
                    <li>GitHub（<a href="https://easystat-4-education.streamlit.app/" target="_blank" style="color: var(--primary-color);">https://easystat-4-education.streamlit.app/</a>）</li>
                    <li>Huggingface（<a href="https://huggingface.co/spaces/itou-daiki/easy_stat" target="_blank" style="color: var(--primary-color);">https://huggingface.co/spaces/itou-daiki/easy_stat</a>）</li>
                    <li>分析に変数選択に制限を設けました</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2023/10/28</div>
            <div class="update-content">
                <ul>
                    <li>一要因分散分析（対応なし）を実装しました。</li>
                    <li>グラフタイトルの表示の有無を選択する機能を実装しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2023/10/26</div>
            <div class="update-content">
                <ul>
                    <li>データクレンジングページを実装しました。</li>
                    <li>t検定で出力される図に、ブラケットと判定を表示できるようにしました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2023/10/25</div>
            <div class="update-content">
                <ul>
                    <li>テキストマイニングを実装しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2023/10/24</div>
            <div class="update-content">
                <ul>
                    <li>探索的データ分析（EDA）を実装しました。</li>
                    <li>相関分析を修正しました。</li>
                    <li>カイ２乗分析を修正しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2023/09/01</div>
            <div class="update-content">
                <ul>
                    <li>リポジトリを移動しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2023/08/01</div>
            <div class="update-content">
                <ul>
                    <li>簡易データサイエンス機能を実装しました。</li>
                    <li>UIとその他の軽微な修正を行いました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2023/03/11</div>
            <div class="update-content">
                <ul>
                    <li>相関分析機能を実装しました。</li>
                </ul>
            </div>
        </div>
        <div class="update-item">
            <div class="update-date">2023/03/06</div>
            <div class="update-content">
                <ul>
                    <li>ｔ検定（対応あり・なし）を統合しました。</li>
                </ul>
            </div>
        </div>
    </div>
</div>
""")

# リンク・連絡先情報
st.html('<div class="section fade-in">')
common.display_link()
st.html('</div>')

# その他の表示
common.display_copyright()
common.display_special_thanks()

# メインコンテナ終了
st.html('</div>')
