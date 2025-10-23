# AI統計解釈機能 統合ガイド

## 概要
このガイドは、Easy Statの各分析モジュールにAI統計解釈機能を追加する方法を説明します。

## 実装済みの機能

### 1. 共通モジュール (`common.py`)
- `AIStatisticalInterpreter`クラス: AI解釈機能の中核
- Gemini 2.0 Flash API統合
- 以下の分析タイプに対応したプロンプトテンプレート:
  - 相関分析 (`correlation`)
  - カイ二乗検定 (`chi_square`)
  - t検定 (`ttest`)
  - 分散分析 (`anova`)

### 2. 実装済み分析モジュール
- ✅ **03_カイ２乗検定.py** - 完全実装
- ✅ **02_相関分析.py** - 完全実装

## 実装方法

### ステップ1: サイドバーにAI機能を追加

各分析ページの冒頭（`st.title()`の後）に以下を追加:

```python
# AI解釈機能の設定
gemini_api_key, enable_ai_interpretation = common.AIStatisticalInterpreter.setup_ai_sidebar()
```

### ステップ2: 分析結果をまとめる

分析実行後、結果を辞書形式でまとめます:

#### カイ二乗検定の例:
```python
chi_square_results = {
    'chi2': chi2,
    'p_value': p_value,
    'dof': dof,
    'var1': selected_col1,
    'var2': selected_col2,
    'crosstab': crosstab.iloc[:-1, :-1],
    'expected': expected_df
}
```

#### 相関分析の例:
```python
correlation_results = {
    'correlation': r,
    'p_value': p_value,
    'var1': var1,
    'var2': var2,
    'sample_size': n
}
```

#### t検定の例:
```python
ttest_results = {
    't_statistic': t_stat,
    'p_value': p_value,
    'dof': dof,
    'mean1': mean1,
    'mean2': mean2,
    'std1': std1,
    'std2': std2,
    'n1': n1,
    'n2': n2,
    'effect_size': cohen_d,
    'test_type': 't検定（対応なし）',
    'group1_name': group1,
    'group2_name': group2
}
```

#### 分散分析の例:
```python
anova_results = {
    'f_statistic': f_stat,
    'p_value': p_value,
    'df_between': df_between,
    'df_within': df_within,
    'group_means': group_means_dict,
    'eta_squared': eta_squared,
    'analysis_type': '一要因分散分析（対応なし）'
}
```

### ステップ3: AI解釈を表示

結果の表示後、以下のコードを追加:

```python
# AI解釈機能の追加
if gemini_api_key and enable_ai_interpretation:
    # 結果をまとめる
    results = {
        # ステップ2で作成した辞書
    }

    # AI解釈を表示
    common.AIStatisticalInterpreter.display_ai_interpretation(
        api_key=gemini_api_key,
        enabled=enable_ai_interpretation,
        results=results,
        analysis_type='correlation',  # or 'chi_square', 'ttest', 'anova'
        key_prefix=f'unique_key_for_this_analysis'
    )
```

## 各分析モジュールへの適用

### t検定（対応なし） - `04_t検定（対応なし）.py`

1. **追加位置**: t検定結果の表示後
2. **必要なデータ**:
   - t統計量、p値、自由度
   - 各グループの平均値、標準偏差、サンプルサイズ
   - Cohen's d（効果量）
3. **analysis_type**: `'ttest'`

### t検定（対応あり） - `05_t検定（対応あり）.py`

1. **追加位置**: t検定結果の表示後
2. **必要なデータ**: 対応なしと同様
3. **test_type**: `'t検定（対応あり）'`

### 一要因分散分析（対応なし） - `06_一要因分散分析（対応なし）.py`

1. **追加位置**: 分散分析結果の表示後
2. **必要なデータ**:
   - F統計量、p値、自由度（群間・群内）
   - 各グループの平均値
   - 効果量（η²）
3. **analysis_type**: `'anova'`

### 一要因分散分析（対応あり） - `07_一要因分散分析（対応あり）.py`

同様の実装パターン

### 二要因分散分析 - `08_二要因分散分析（対応なし）.py`

より複雑なプロンプトが必要な場合、`common.py`に専用メソッドを追加:

```python
@staticmethod
def create_two_way_anova_interpretation_prompt(anova_results: Dict[str, Any]) -> str:
    # 主効果と交互作用を含むプロンプトを作成
    pass
```

### 回帰分析 - `10_単回帰分析.py`, `11_重回帰分析.py`

**重回帰分析は既に実装済み**（元のコードを参照）

単回帰分析には同様のパターンで実装可能。

### 因子分析・主成分分析 - `12_因子分析.py`, `13_主成分分析.py`

これらの分析には専用のプロンプトテンプレートが必要です。
`common.py`に以下を追加:

```python
@staticmethod
def create_factor_analysis_interpretation_prompt(results: Dict[str, Any]) -> str:
    """因子分析の解釈プロンプト"""
    # 因子負荷量、寄与率、因子の解釈などを含む
    pass

@staticmethod
def create_pca_interpretation_prompt(results: Dict[str, Any]) -> str:
    """主成分分析の解釈プロンプト"""
    # 主成分負荷量、寄与率、主成分の解釈などを含む
    pass
```

## ベストプラクティス

### 1. エラーハンドリング

必ずエラーハンドリングを実装:

```python
try:
    # 分析実行
    # AI解釈実行
except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")
```

### 2. セッション状態の管理

解釈結果は自動的にセッション状態に保存されます。
ユーザーは「解釈をクリア」ボタンで結果をリセットできます。

### 3. ユニークなキー

`key_prefix`は必ずユニークにしてください:

```python
key_prefix=f'{analysis_type}_{var1}_{var2}_{timestamp}'
```

### 4. APIキーの保護

APIキーは`type="password"`で入力され、平文では表示されません。

## テスト方法

1. Google AI Studioでテスト用APIキーを取得
2. デモデータで各分析を実行
3. AI解釈ボタンをクリック
4. 結果が適切に表示されることを確認

## トラブルシューティング

### APIエラー
- APIキーが有効か確認
- API制限に達していないか確認
- インターネット接続を確認

### 表示されない
- `gemini_api_key`と`enable_ai_interpretation`が正しく取得されているか確認
- `key_prefix`が他と重複していないか確認

### プロンプトが不適切
- `common.py`のプロンプトテンプレートを調整
- 結果の辞書に必要なデータがすべて含まれているか確認

## 今後の拡張

### 他のAIモデルへの対応
`AIStatisticalInterpreter`に他のAPIメソッドを追加:

```python
@staticmethod
def call_openai_api(api_key: str, prompt: str) -> str:
    # OpenAI API実装
    pass

@staticmethod
def call_claude_api(api_key: str, prompt: str) -> str:
    # Claude API実装
    pass
```

### カスタムプロンプト
ユーザーがプロンプトをカスタマイズできる機能を追加。

## まとめ

このガイドに従うことで、すべての分析モジュールに一貫したAI解釈機能を追加できます。
主要な実装は`common.py`に集約されているため、メンテナンスも容易です。
