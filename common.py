import matplotlib.pyplot as plt
import os
import streamlit as st
import japanize_matplotlib
import matplotlib.font_manager as font_manager
import pandas as pd
import numpy as np
from scipy import stats
import warnings
from typing import Optional, Dict, Any, Tuple


def display_header():
    st.caption('Created by Dit-Lab.(Daiki Ito)')


def set_font():
    # font_path = '../ipaexg.ttf'  # pages フォルダから一つ上を見る
    font_path = os.path.join(os.path.dirname(__file__), '..', 'ipaexg.ttf')

    plt.rcParams['font.family'] = 'IPAexGothic'


def display_guide():
    st.markdown("""
    - [**情報探究ステップアップガイド**](https://dit-lab.notion.site/612d9665350544aa97a2a8514a03c77c?v=85ad37a3275b4717a0033516b9cfd9cc)
    - [**中の人のページ（Dit-Lab.）**](https://dit-lab.notion.site/Dit-Lab-da906d09d3cf42a19a011cf4bf25a673?pvs=4)
    """)


def display_link():
    st.header('リンク')
    st.markdown("""
    - [**中の人のページ（Dit-Lab.）**](https://dit-lab.notion.site/Dit-Lab-da906d09d3cf42a19a011cf4bf25a673?pvs=4)
    - [**進数変換学習アプリ**](https://easy-base-converter.streamlit.app)
    - [**easyRSA**](https://easy-rsa.streamlit.app/)
    - [**easyAutoML（回帰）**](https://huggingface.co/spaces/itou-daiki/pycaret_datascience_streamlit)
    - [**pkl_predict_reg**](https://huggingface.co/spaces/itou-daiki/pkl_predict_reg)
    - [**音のデータサイエンス**](https://audiovisualizationanalysis-bpeekdjwymuf6nkqcb4cqy.streamlit.app)
    - [**3D RGB Cube Visualizer**](https://boxplot-4-mysteams.streamlit.app)
    - [**上マーク角度計算補助ツール**](https://sailing-mark-angle.streamlit.app)
    - [**Factor Score Calculator**](https://factor-score-calculator.streamlit.app/)
    - [**easy Excel Merge**](https://easy-xl-merge.streamlit.app)
    - [**フィードバックはこちらまで**](https://forms.gle/G5sMYm7dNpz2FQtU9)
    - [**ソースコードはこちら（GitHub）**](https://github.com/itou-daiki/easy_stat)
    """)


def display_copyright():
    st.subheader('')
    st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
    st.write('')
    st.subheader('© 2022-2025 Dit-Lab.(Daiki Ito). All Rights Reserved.')
    st.write('easyStat: Open Source for Ubiquitous Statistics')
    st.write('Democratizing data, everywhere.')
    st.write('')


def display_special_thanks():
    st.subheader('In collaboration with our esteemed contributors:')
    st.write('・Toshiyuki')
    st.write('With heartfelt appreciation for their dedication and support.')


# ==========================================
# 統計初学者向け学習支援機能
# ==========================================

class StatisticalLearningAssistant:
    """統計初学者向けの学習支援クラス"""
    
    def __init__(self):
        self.learning_levels = {
            'beginner': '初級者',
            'intermediate': '中級者', 
            'advanced': '上級者'
        }
    
    def show_concept_explanation(self, concept_key: str, level: str = 'beginner'):
        """統計概念の説明を表示"""
        explanations = {
            'correlation': {
                'beginner': """
                📊 **相関分析とは？**
                
                相関分析は、2つの変数がどれくらい関係しているかを調べる分析方法です。
                
                **相関係数の読み方：**
                - 1に近い：強い正の相関（一方が増えると他方も増える）
                - 0に近い：相関なし（関係が薄い）
                - -1に近い：強い負の相関（一方が増えると他方は減る）
                
                **例：** 勉強時間と成績、身長と体重など
                """,
                'intermediate': """
                📊 **相関分析の詳細**
                
                ピアソンの相関係数（r）は線形関係の強さを測定します。
                
                **解釈の目安：**
                - |r| ≥ 0.7：強い相関
                - 0.3 ≤ |r| < 0.7：中程度の相関
                - |r| < 0.3：弱い相関
                
                **注意点：** 相関関係≠因果関係
                """,
                'advanced': """
                📊 **相関分析の統計的詳細**
                
                - ピアソンの積率相関係数：r = Σ[(xi-x̄)(yi-ȳ)] / √[Σ(xi-x̄)²Σ(yi-ȳ)²]
                - 前提条件：正規分布、線形関係、等分散性
                - 有意性検定：t = r√(n-2)/√(1-r²)
                """
            },
            'ttest': {
                'beginner': """
                📊 **t検定とは？**
                
                2つのグループの平均値に違いがあるかを調べる検定です。
                
                **種類：**
                - 対応なし：異なる人たちを比較（例：男性vs女性の身長）
                - 対応あり：同じ人の前後を比較（例：薬の服用前後）
                
                **p値が0.05未満なら「有意な差がある」と判断します**
                """,
                'intermediate': """
                📊 **t検定の詳細**
                
                **前提条件：**
                - データが正規分布に従う
                - 対応なしの場合：等分散性
                - 独立性
                
                **効果量（Cohen's d）：**
                - 0.2：小さい効果
                - 0.5：中程度の効果  
                - 0.8：大きい効果
                """,
                'advanced': """
                📊 **t検定の統計的詳細**
                
                - 対応なし：t = (x̄₁-x̄₂) / SE_diff
                - 対応あり：t = d̄ / (sd/√n)
                - Welchのt検定：等分散性を仮定しない
                - 自由度の調整が重要
                """
            }
        }
        
        if concept_key in explanations and level in explanations[concept_key]:
            st.info(explanations[concept_key][level])
    
    def check_learning_progress(self, analysis_type: str):
        """学習進捗をチェック"""
        if 'learning_progress' not in st.session_state:
            st.session_state.learning_progress = set()
        
        st.session_state.learning_progress.add(analysis_type)
        
        progress_count = len(st.session_state.learning_progress)
        total_analyses = 14  # 総分析数
        
        st.sidebar.success(f"📚 学習進捗: {progress_count}/{total_analyses} 完了")
        
        if progress_count >= total_analyses:
            st.balloons()
            st.success("🎉 すべての分析を体験しました！統計マスターですね！")


# ==========================================
# エラーハンドリング・データ検証フレームワーク
# ==========================================

class StatisticalValidator:
    """統計分析のデータ検証クラス"""
    
    @staticmethod
    def safe_file_load(uploaded_file) -> Optional[pd.DataFrame]:
        """安全なファイル読み込み"""
        try:
            if uploaded_file is None:
                return None
                
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                # CSVの場合、エンコーディングを自動判定
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)  # ファイルポインタをリセット
                    df = pd.read_csv(uploaded_file, encoding='shift_jis')
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(uploaded_file)
            else:
                st.error("⚠️ 対応していないファイル形式です。CSV、Excel(.xlsx/.xls)ファイルをアップロードしてください。")
                return None
            
            # 基本的なデータ検証
            if df.empty:
                st.error("⚠️ アップロードされたファイルにデータが含まれていません。")
                return None
            
            # 列名の日本語対応確認
            if any(col.startswith('Unnamed:') for col in df.columns):
                st.warning("⚠️ 列名が正しく読み込まれていない可能性があります。ファイルの1行目に列名が含まれているか確認してください。")
            
            return df
            
        except Exception as e:
            st.error(f"⚠️ ファイルの読み込み中にエラーが発生しました: {str(e)}")
            st.info("💡 **解決のヒント:**\n- ファイルが破損していないか確認\n- Excel形式の場合は.xlsxで保存\n- CSVの場合は文字コード(UTF-8)を確認")
            return None
    
    @staticmethod
    def validate_sample_size(data: pd.DataFrame, min_size: int = 3, analysis_type: str = "分析") -> bool:
        """サンプルサイズの検証"""
        if len(data) < min_size:
            st.error(f"⚠️ {analysis_type}には最低{min_size}件のデータが必要です。現在のデータ件数: {len(data)}件")
            st.info("💡 **解決方法:** より多くのデータを収集するか、他の分析手法を検討してください。")
            return False
        return True
    
    @staticmethod
    def check_missing_values(data: pd.DataFrame, columns: list) -> Dict[str, Any]:
        """欠損値のチェック"""
        missing_info = {}
        for col in columns:
            if col in data.columns:
                missing_count = data[col].isnull().sum()
                missing_info[col] = missing_count
                
                if missing_count > 0:
                    st.warning(f"⚠️ 変数「{col}」に{missing_count}件の欠損値があります。")
        
        total_missing = sum(missing_info.values())
        if total_missing > 0:
            st.info("💡 **欠損値の対処法:**\n- データクレンジングページで欠損値を処理\n- 欠損値のある行を除外\n- 平均値や中央値で補完")
        
        return missing_info
    
    @staticmethod
    def validate_data_types(data: pd.DataFrame, columns: list, expected_type: str = 'numeric') -> bool:
        """データ型の検証"""
        valid = True
        for col in columns:
            if col in data.columns:
                if expected_type == 'numeric':
                    if not pd.api.types.is_numeric_dtype(data[col]):
                        st.error(f"⚠️ 変数「{col}」は数値型である必要があります。現在の型: {data[col].dtype}")
                        st.info("💡 **解決方法:** データクレンジングページで数値型に変換してください。")
                        valid = False
        return valid
    
    @staticmethod
    def check_normality(data: pd.Series, alpha: float = 0.05) -> Dict[str, Any]:
        """正規性の検定"""
        if len(data.dropna()) < 3:
            return {'test': 'insufficient_data', 'p_value': None, 'is_normal': False}
        
        # Shapiro-Wilk検定（サンプルサイズが小さい場合）
        if len(data.dropna()) <= 50:
            stat, p_value = stats.shapiro(data.dropna())
            test_name = 'Shapiro-Wilk'
        else:
            # Kolmogorov-Smirnov検定（サンプルサイズが大きい場合）
            stat, p_value = stats.kstest(data.dropna(), 'norm')
            test_name = 'Kolmogorov-Smirnov'
        
        is_normal = p_value > alpha
        return {
            'test': test_name,
            'statistic': stat,
            'p_value': p_value,
            'is_normal': is_normal
        }
    
    @staticmethod
    def check_equal_variances(group1: pd.Series, group2: pd.Series, alpha: float = 0.05) -> Dict[str, Any]:
        """等分散性の検定（Levene検定）"""
        try:
            stat, p_value = stats.levene(group1.dropna(), group2.dropna())
            equal_variances = p_value > alpha
            return {
                'statistic': stat,
                'p_value': p_value,
                'equal_variances': equal_variances
            }
        except Exception as e:
            return {'error': str(e), 'equal_variances': False}


# ==========================================
# 結果解釈支援機能
# ==========================================

class ResultInterpreter:
    """統計結果の解釈支援クラス"""
    
    @staticmethod
    def interpret_correlation(r: float, p_value: float, alpha: float = 0.05) -> str:
        """相関係数の解釈"""
        # 相関の強さ
        abs_r = abs(r)
        if abs_r >= 0.7:
            strength = "強い"
        elif abs_r >= 0.3:
            strength = "中程度の"
        else:
            strength = "弱い"
        
        # 相関の方向
        direction = "正の" if r > 0 else "負の"
        
        # 有意性
        significance = "統計的に有意" if p_value < alpha else "統計的に有意ではない"
        
        interpretation = f"""
        📊 **結果の解釈**
        
        - **相関の強さ**: {strength}相関 (r = {r:.3f})
        - **相関の方向**: {direction}相関
        - **統計的有意性**: {significance} (p = {p_value:.3f})
        
        **実際の意味**:
        """
        
        if abs_r >= 0.7 and p_value < alpha:
            interpretation += "2つの変数には強い関係があります。一方が変化すると他方も予測可能な形で変化する傾向があります。"
        elif abs_r >= 0.3 and p_value < alpha:
            interpretation += "2つの変数にはある程度の関係があります。完全ではありませんが、関連性が認められます。"
        elif p_value >= alpha:
            interpretation += "統計的に有意な関係は認められませんでした。偶然による結果の可能性があります。"
        else:
            interpretation += "関係はあるものの弱く、実際の予測や判断には注意が必要です。"
        
        return interpretation
    
    @staticmethod
    def interpret_ttest(t_stat: float, p_value: float, effect_size: float, alpha: float = 0.05) -> str:
        """t検定結果の解釈"""
        significance = "統計的に有意" if p_value < alpha else "統計的に有意ではない"
        
        # 効果量の解釈
        if abs(effect_size) >= 0.8:
            effect_interpretation = "大きい効果"
        elif abs(effect_size) >= 0.5:
            effect_interpretation = "中程度の効果"
        elif abs(effect_size) >= 0.2:
            effect_interpretation = "小さい効果"
        else:
            effect_interpretation = "効果はほとんどない"
        
        interpretation = f"""
        📊 **結果の解釈**
        
        - **統計的有意性**: {significance} (p = {p_value:.3f})
        - **効果量**: {effect_interpretation} (Cohen's d = {effect_size:.3f})
        - **t統計量**: {t_stat:.3f}
        
        **結論**:
        """
        
        if p_value < alpha:
            interpretation += f"2つのグループ間に{effect_interpretation}な差があることが統計的に確認されました。"
        else:
            interpretation += "2つのグループ間に統計的に有意な差は認められませんでした。"
        
        return interpretation


# ==========================================
# インタラクティブ学習ガイド
# ==========================================

def show_interactive_guide(analysis_type: str):
    """インタラクティブな学習ガイドを表示"""
    guides = {
        'correlation': {
            'title': '🔍 相関分析学習ガイド',
            'steps': [
                "1️⃣ データをアップロードしましょう",
                "2️⃣ 分析したい2つの変数を選択します",
                "3️⃣ 散布図で視覚的に関係を確認",
                "4️⃣ 相関係数を計算・解釈",
                "5️⃣ 結果をレポートにまとめる"
            ],
            'tips': [
                "💡 まずは散布図で直線的な関係があるか確認",
                "💡 外れ値がないかチェック",
                "💡 相関≠因果関係を忘れずに"
            ]
        },
        'ttest': {
            'title': '📊 t検定学習ガイド',
            'steps': [
                "1️⃣ 比較したいグループを明確にする",
                "2️⃣ データの正規性を確認",
                "3️⃣ 等分散性をチェック（対応なしの場合）",
                "4️⃣ 適切なt検定を実行",
                "5️⃣ 効果量も含めて解釈"
            ],
            'tips': [
                "💡 対応あり・なしの選択が重要",
                "💡 p値だけでなく効果量も確認",
                "💡 実際的な意味を考える"
            ]
        }
    }
    
    if analysis_type in guides:
        guide = guides[analysis_type]
        
        with st.expander(f"{guide['title']} - クリックして展開"):
            st.markdown("### 📋 学習ステップ")
            for step in guide['steps']:
                st.markdown(step)
            
            st.markdown("### 💡 重要なポイント")
            for tip in guide['tips']:
                st.markdown(tip)
            
            # 学習チェックリスト
            st.markdown("### ✅ 学習チェックリスト")
            for i, step in enumerate(guide['steps']):
                completed = st.checkbox(f"完了: {step}", key=f"checklist_{analysis_type}_{i}")


def show_beginner_tips():
    """初学者向けのヒントを表示"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎓 統計学習のコツ")
    
    tips = [
        "📊 まずはグラフで視覚化",
        "🔢 数値だけでなく意味も考える", 
        "❓ 「なぜ？」を常に問いかける",
        "📈 複数の分析を組み合わせる",
        "📝 結果を文章で説明してみる"
    ]
    
    for tip in tips:
        st.sidebar.markdown(f"- {tip}")


def create_learning_dashboard():
    """学習ダッシュボードを作成"""
    if 'learning_progress' not in st.session_state:
        st.session_state.learning_progress = set()
    
    progress = st.session_state.learning_progress
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 学習進捗ダッシュボード")
    
    analyses = [
        "データクレンジング", "EDA", "相関分析", "カイ二乗検定",
        "t検定（対応なし）", "t検定（対応あり）", "一要因分散分析（対応なし）",
        "一要因分散分析（対応あり）", "二要因分散分析", "二要因混合分散分析",
        "単回帰分析", "重回帰分析", "因子分析", "テキストマイニング"
    ]
    
    completed_count = len(progress)
    total_count = len(analyses)
    progress_percentage = (completed_count / total_count) * 100
    
    st.sidebar.progress(progress_percentage / 100)
    st.sidebar.markdown(f"**進捗: {completed_count}/{total_count} ({progress_percentage:.1f}%)**")
    
    if completed_count == total_count:
        st.sidebar.success("🏆 全分析制覇！")
    elif completed_count >= total_count // 2:
        st.sidebar.info("📈 中級者レベル達成！")
    elif completed_count >= 3:
        st.sidebar.info("🌱 順調に学習中！")
