# Easy Stat - 統計分析アプリケーション

日本語対応のStreamlitベース統計分析アプリケーションです。

## プロジェクト構成
- `TOP.py` - メインアプリケーションのエントリーポイント
- `common.py` - 共通のユーティリティと関数
- `pages/` - 個別の分析モジュール（00-14）
- `datasets/` - デモンストレーション用サンプルデータセット
- `images/` - 分析手法の説明画像
- `requirements.txt` - Python依存関係

## アプリケーションの実行
```bash
pip install -r requirements.txt
streamlit run TOP.py
```

## 分析機能
- データクレンジングと探索的データ分析（EDA）
- 相関分析
- カイ二乗検定
- t検定（対応あり・なし）
- 分散分析（一要因・二要因・混合）
- 回帰分析
- 因子分析
- 主成分分析
- テキストマイニング

## デプロイメント

### Streamlit Share
1. GitHubリポジトリをパブリックに設定
2. https://share.streamlit.io/ にアクセス
3. リポジトリを選択してデプロイ
4. メインファイル: `TOP.py`
5. Python バージョン: 3.9+

### Hugging Face Spaces
1. https://huggingface.co/spaces にアクセス
2. 新しいSpaceを作成（SDK: Streamlit）
3. リポジトリファイルをアップロード
4. `app.py`として`TOP.py`をリネーム、または`app_file`を`TOP.py`に設定

## 依存関係
データ分析、可視化、日本語テキスト処理のためのライブラリ（pandas、numpy、matplotlib、seaborn、scipy、scikit-learn、日本語フォントサポート等）を使用しています。