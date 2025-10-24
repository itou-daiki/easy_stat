from itertools import combinations
from statistics import median, variance

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st
from PIL import Image
from scipy import stats
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.multitest import multipletests

import common


st.set_page_config(page_title="一要因分散分析（対応あり）", layout="wide")

# AI解釈機能の設定
gemini_api_key, enable_ai_interpretation = common.AIStatisticalInterpreter.setup_ai_sidebar()

st.title("一要因分散分析（対応あり）")
common.display_header()
st.write("各時点（例：前・中・後）の変容について検定を行います。")
st.write("※各行は１被験者のデータとし、識別子は自動生成されます。")

# 分析イメージ（必要に応じて画像パスを調整）
try:
    image = Image.open('images/anova_rel.png')
    st.image(image)
except Exception as e:
    st.write("※画像が読み込めませんでした。")

# ファイルアップローダー（Excel, CSV, テキスト）
uploaded_file = st.file_uploader("CSV、Excel、またはテキストファイルを選択してください",
                                 type=["csv", "xlsx", "txt"])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    try:
        df = pd.read_excel('datasets/anova_demo_rel.xlsx', sheet_name=0)
        st.write("【デモデータ】")
        st.write(df.head())
    except FileNotFoundError:
        st.error("デモデータファイルが見つかりません。ファイルパスを確認してください。")
else:
    if uploaded_file is not None:
        try:
            if uploaded_file.type == 'text/plain':
                df = pd.read_csv(uploaded_file, delim_whitespace=True)
            elif uploaded_file.type == 'text/csv':
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.write("【アップロードデータ】")
            st.write(df.head())
        except Exception as e:
            st.error(f"ファイル読み込み中にエラーが発生しました: {e}")

if df is not None:
    st.subheader("検定対象の変数の選択")
    st.write("※各列は１被験者の各時点の測定値とみなします。")
    # 数値型の列一覧から、検定対象の変数をマルチセレクト（最低３項目以上）
    numeric_options = df.select_dtypes(include=['number']).columns.tolist()
    selected_vars = st.multiselect('検定対象の数値変数を選択してください（３項目以上）', 
                                   options=numeric_options)
    
    if len(selected_vars) < 3:
        st.error("３つ以上の変数を選択してください。")
    else:
        # 被験者識別子を自動追加（各行を１被験者とする）
        df = df.copy()
        df.insert(0, '被験者識別子', np.arange(1, len(df)+1))
        
        # ワイド形式からロング形式に変換（※表示はしません）
        df_long = pd.melt(df, id_vars=['被験者識別子'], value_vars=selected_vars, 
                          var_name='条件', value_name='測定値')
        
        # ----------------------------
        # 要約統計量の表示
        # ----------------------------
        st.subheader("【要約統計量】")
        summary_df = df_long.groupby('条件')['測定値'].agg(
            有効N = 'count',
            平均値 = 'mean',
            中央値 = 'median',
            標準偏差 = lambda x: x.std(ddof=1),
            分散 = lambda x: x.var(ddof=1),
            最小値 = 'min',
            最大値 = 'max'
        ).reset_index()
        st.write(summary_df.style.format({
            '平均値': "{:.2f}",
            '中央値': "{:.2f}",
            '標準偏差': "{:.2f}",
            '分散': "{:.2f}",
            '最小値': "{:.2f}",
            '最大値': "{:.2f}"
        }))

        # ----------------------------
        # 繰り返し測定ANOVA（対応のある分散分析）の実行
        # ----------------------------
        st.subheader("【分散分析（対応あり）】")
        try:
            aovrm = AnovaRM(df_long, depvar='測定値', subject='被験者識別子', within=['条件'])
            res = aovrm.fit()
            # anova_tableをデータフレームとして表示
            st.dataframe(res.anova_table.style.format("{:.2f}"))
        except Exception as e:
            st.error(f"分散分析の実行中にエラーが発生しました: {e}")

        # ----------------------------
        # 多重比較（各条件間の対応のある t 検定＋ボンフェローニ補正）
        # ----------------------------
        st.subheader("【多重比較の結果】")
        try:
            levels = df_long['条件'].unique()
            pairwise_results = []
            # 全組み合わせに対して対応のある t 検定を実施
            for (level1, level2) in combinations(levels, 2):
                data1 = df_long[df_long['条件'] == level1][['被験者識別子', '測定値']]
                data2 = df_long[df_long['条件'] == level2][['被験者識別子', '測定値']]
                merged = pd.merge(data1, data2, on='被験者識別子', suffixes=('_1', '_2'))
                t_stat, p_val = stats.ttest_rel(merged['測定値_1'], merged['測定値_2'])
                pairwise_results.append([level1, level2, t_stat, p_val])
            
            # ボンフェローニ補正
            p_vals = [row[3] for row in pairwise_results]
            reject, pvals_corrected, _, _ = multipletests(p_vals, method='bonferroni')
            
            # 判定：p補正値 < 0.01 → "**", < 0.05 → "*", < 0.1 → "†", それ以外は "n.s."
            for i, row in enumerate(pairwise_results):
                row.append(pvals_corrected[i])
                p_adj = pvals_corrected[i]
                if p_adj < 0.01:
                    judgement = '**'
                elif p_adj < 0.05:
                    judgement = '*'
                elif p_adj < 0.1:
                    judgement = '†'
                else:
                    judgement = 'n.s.'
                row.append(judgement)
            pairwise_df = pd.DataFrame(pairwise_results, 
                                       columns=['Level1', 'Level2', 't-stat', 'p-value', 'p-value (補正後)', '判定'])
            st.write(pairwise_df.style.format({
                't-stat': "{:.2f}",
                'p-value': "{:.2f}",
                'p-value (補正後)': "{:.2f}"
            }))
        except Exception as e:
            st.error(f"多重比較の実行中にエラーが発生しました: {e}")

        # ----------------------------
        # サンプルサイズの表示
        # ----------------------------
        st.subheader("【サンプルサイズ】")
        st.write(f"全体のデータ数（行数）： {len(df)}")
        subjects = df['被験者識別子'].unique()
        st.write(f"被験者数： {len(subjects)}")

        # ----------------------------
        # 可視化（各条件ごとの平均値と標準誤差＋ブラケット・アノテーション付き）
        # ----------------------------
        st.subheader("【可視化】")
        show_graph_title = st.checkbox('グラフタイトルを表示する', value=True)
        
        group_stats = df_long.groupby('条件')['測定値'].agg(['mean', 'sem']).reset_index()
        categories = group_stats['条件'].tolist()
        category_positions = {cat: i for i, cat in enumerate(categories)}
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[category_positions[cat] for cat in categories],
            y=group_stats['mean'],
            error_y=dict(type='data', array=group_stats['sem'], visible=True),
            marker_color='skyblue'
        ))
        fig.update_xaxes(
            tickvals=list(category_positions.values()),
            ticktext=list(category_positions.keys())
        )
        if show_graph_title:
            fig.update_layout(title_text="各条件ごとの平均値と標準誤差")
        
        # 補助関数（ブラケットとアノテーション）
        def create_bracket_annotation(x0, x1, y, text):
            return dict(
                xref='x',
                yref='y',
                x=(x0 + x1) / 2,
                y=y,
                text=text,
                showarrow=False,
                font=dict(color='black'),
                xanchor='center',
                yanchor='bottom'
            )

        def create_bracket_shape(x0, x1, y_vline_bottom, bracket_y):
            return dict(
                type='path',
                path=f'M {x0},{y_vline_bottom} L{x0},{bracket_y} L{x1},{bracket_y} L{x1},{y_vline_bottom}',
                line=dict(color='black'),
                xref='x',
                yref='y'
            )

        def assign_levels(comparisons, category_positions):
            # カテゴリの位置を取得
            cat_positions = category_positions
            
            # 各比較を位置でソート（左端の位置、次に幅）
            sorted_comparisons = []
            for comp in comparisons:
                pos1 = cat_positions[comp[0]]
                pos2 = cat_positions[comp[1]]
                left = min(pos1, pos2)
                right = max(pos1, pos2)
                sorted_comparisons.append((left, right, comp))
            
            # 幅の狭い順にソート（狭いものを下のレベルに配置）
            sorted_comparisons.sort(key=lambda x: x[1] - x[0], reverse=False)
            
            # レベルを割り当て
            levels = []
            comparison_levels = []
            
            for left, right, comp in sorted_comparisons:
                # 利用可能な最も低いレベルを見つける
                assigned_level = None
                for level_idx, level_ranges in enumerate(levels):
                    # このレベルで重なりがないかチェック
                    can_place = True
                    margin = 0.5  # ブラケット間のマージン（視覚的な分離を確保）
                    for existing_left, existing_right in level_ranges:
                        # ブラケットが重なるかチェック（マージンを考慮）
                        if not (right + margin <= existing_left or left - margin >= existing_right):
                            can_place = False
                            break
                    
                    if can_place:
                        level_ranges.append((left, right))
                        assigned_level = level_idx
                        break
                
                # 新しいレベルが必要な場合
                if assigned_level is None:
                    levels.append([(left, right)])
                    assigned_level = len(levels) - 1
                
                comparison_levels.append((comp, assigned_level))
            
            # 元の順序に戻す
            result_levels = []
            for comp in comparisons:
                for c, level in comparison_levels:
                    if c == comp:
                        result_levels.append(level)
                        break
            
            return result_levels, len(levels)
        
        # 棒グラフの上限を計算（群の数とレベル数に応じて動的に調整）
        base_y_max = (group_stats['mean'] + group_stats['sem']).max() * 1.1
        num_groups = len(group_stats)

        # オフセットとステップサイズを群数とレベル数に応じて調整
        y_offset = base_y_max * max(0.06, 0.15 / num_groups)  # 群が多いほど相対的に小さく
        step_size = base_y_max * max(0.10, 0.25 / num_groups)  # 群が多いほど相対的に小さく
        
        # 多重比較で有意な比較結果があれば、ブラケット描画のためレベルを割り当て
        if 'significant_comparisons' in locals() or 'pairwise_df' in locals():
            # ここでは、先ほど抽出した有意な比較結果（p補正値 < 0.1）を利用する
            significant_comparisons = []
            for _, row in pairwise_df.iterrows():
                if row['判定'] != 'n.s.':
                    significant_comparisons.append((row['Level1'], row['Level2'], row['p-value (補正後)'], row['判定']))
        else:
            significant_comparisons = []
        
        if significant_comparisons:
            comp_list = [(comp[0], comp[1]) for comp in significant_comparisons]
            comparison_levels, num_levels = assign_levels(comp_list, category_positions)

            # レベル数が多い場合はさらに調整
            if num_levels > 3:
                step_size = step_size * (1 + (num_levels - 3) * 0.1)
        else:
            comparison_levels, num_levels = ([], 0)
        additional_height = num_levels * step_size + y_offset * 2.5
        y_max = base_y_max + additional_height
        
        # アノテーション配置の調整係数（群数に応じて動的に調整）
        vline_bottom_factor = max(0.3, 0.8 / num_groups)  # ブラケット下端の余白
        bracket_offset_factor = max(0.2, 0.5 / num_groups)  # ブラケット上端の追加余白
        annotation_offset_factor = max(0.3, 0.8 / num_groups)  # アノテーションの余白

        if significant_comparisons:
            for idx, (group1, group2, p_value, sign) in enumerate(significant_comparisons):
                x0 = category_positions[group1]
                x1 = category_positions[group2]
                y_vline_bottom = max(
                    group_stats[group_stats['条件'] == group1]['mean'].values[0] + group_stats[group_stats['条件'] == group1]['sem'].values[0],
                    group_stats[group_stats['条件'] == group2]['mean'].values[0] + group_stats[group_stats['条件'] == group2]['sem'].values[0]
                ) + y_offset * vline_bottom_factor
                level = comparison_levels[idx]
                bracket_y = y_vline_bottom + (level * step_size) + y_offset * bracket_offset_factor
                fig.add_shape(create_bracket_shape(x0, x1, y_vline_bottom, bracket_y))
                annotation_y = bracket_y + y_offset * annotation_offset_factor
                fig.add_annotation(create_bracket_annotation(x0, x1, annotation_y, f"p < {p_value:.2f} {sign}"))
        
        fig.update_yaxes(range=[0, y_max * 1.05])
        fig.update_layout(font=dict(family="IPAexGothic"))
        st.plotly_chart(fig, use_container_width=True)

        # Excelダウンロードリンク
        excel_data = common.export_plotly_to_excel(fig, filename="一要因分散分析対応あり.xlsx", sheet_name="グラフ")
        import base64
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="一要因分散分析対応あり.xlsx" style="text-decoration: none; color: #1f77b4;">📊 グラフをExcelでダウンロード</a>'
        st.markdown(href, unsafe_allow_html=True)

        caption_text = "各条件ごとの平均値 (SE): " + ", ".join(
            [f"{row['条件']}: {row['mean']:.2f} ({row['sem']:.2f})" for _, row in group_stats.iterrows()]
        )
        st.caption(caption_text)

        # ----------------------------
        # 解釈の補助（全体の効果）
        # ----------------------------
        st.subheader("【解釈の補助】")
        try:
            p_value_overall = res.anova_table['Pr > F'][0]
            f_value_overall = res.anova_table['F Value'][0]
            df_num = res.anova_table['Num DF'][0]
            df_den = res.anova_table['Den DF'][0]

            if p_value_overall < 0.01:
                significance_overall = "有意な差が生まれる"
                sign_overall = '**'
            elif p_value_overall < 0.05:
                significance_overall = "有意な差が生まれる"
                sign_overall = '*'
            elif p_value_overall < 0.1:
                significance_overall = "有意な差が生まれる傾向にある"
                sign_overall = '†'
            else:
                significance_overall = "有意な差が生まれない"
                sign_overall = 'n.s.'
            st.write(f"各条件間で、全体として {significance_overall} （ p = {p_value_overall:.3f} {sign_overall} ）")

            # AI解釈機能を追加
            if enable_ai_interpretation and gemini_api_key:
                # 各条件の平均値を辞書形式で取得
                group_means = {}
                for cond in df_long['条件'].unique():
                    cond_mean = df_long[df_long['条件'] == cond]['測定値'].mean()
                    group_means[str(cond)] = cond_mean

                anova_results = {
                    'f_statistic': f_value_overall,
                    'p_value': p_value_overall,
                    'df_between': df_num,
                    'df_within': df_den,
                    'group_means': group_means,
                    'eta_squared': 0.0,  # 一要因対応ありの場合は効果量が別途計算される
                    'analysis_type': '一要因分散分析（対応あり）'
                }
                common.AIStatisticalInterpreter.display_ai_interpretation(
                    api_key=gemini_api_key,
                    enabled=enable_ai_interpretation,
                    results=anova_results,
                    analysis_type='anova',
                    key_prefix='anova_rm_overall'
                )
        except Exception as e:
            st.error(f"解釈の補助の実行中にエラーが発生しました: {e}")
        
        # ----------------------------
        # 解釈の補助（多重比較の結果）
        # ----------------------------
        st.subheader("【多重比較の解釈】")
        if not pairwise_df.empty:
            for idx, row in pairwise_df.iterrows():
                sign = row['判定']
                if sign in ['**', '*']:
                    significance = "有意な差が生まれる"
                elif sign == '†':
                    significance = "有意な差が生まれる傾向にある"
                else:
                    significance = "有意な差が生まれない"
                st.write(f"条件【{row['Level1']} vs {row['Level2']}】では、{significance}（補正後 p = {row['p-value (補正後)']:.2f}、判定: {sign} ）")
        else:
            st.write("多重比較の結果、特に有意な差は認められませんでした。")

# フッター
common.display_copyright()
common.display_special_thanks()
