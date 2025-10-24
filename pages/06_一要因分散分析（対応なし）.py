from statistics import median, variance

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

import common


st.set_page_config(page_title="一要因分散分析(対応なし)", layout="wide")

st.title("一要因分散分析(対応なし)")
common.display_header()
st.write("変数の選択　→　分散分析　→　表作成　→　解釈の補助を行います")
st.write("")

# 分析のイメージ
image = Image.open('images/anova.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    try:
        df = pd.read_excel('datasets/anova_demo.xlsx', sheet_name=0)
        st.write(df.head())
    except FileNotFoundError:
        st.error("デモデータファイルが見つかりません。ファイルパスを確認してください。")
else:
    if uploaded_file is not None:
        try:
            if uploaded_file.type == 'text/csv':
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.write(df.head())
        except Exception as e:
            st.error(f"ファイルの読み込み中にエラーが発生しました: {e}")

if df is not None:
    # カテゴリ変数の抽出
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    # 数値変数の抽出
    numerical_cols = df.select_dtypes(exclude=['object', 'category']).columns.tolist()

    # カテゴリ変数の選択
    st.subheader("カテゴリ変数の選択")
    cat_var = st.multiselect('カテゴリ変数を選択してください', categorical_cols, max_selections=1)

    # 数値変数の選択
    st.subheader("数値変数の選択")
    num_vars = st.multiselect('数値変数を選択してください', numerical_cols)

    # エラー処理
    if not cat_var:
        st.error("カテゴリ変数を選択してください。")
    elif not num_vars:
        st.error("数値変数を選択してください。")
    elif len(df[cat_var].iloc[:, 0].unique()) < 3:
        st.error("独立変数が3群以上になっていないため、分析を実行できません")
    else:
        st.success("分析可能な変数を選択しました。分析を実行します。")

        # 独立変数から重複のないデータを抽出し、リストに変換
        xcat_var_d = df[cat_var].iloc[:, 0].unique().tolist()
        st.subheader('【分析前の確認】')
        cat_var_str = cat_var[0]

        # xcat_var_dの要素をst.writeで表示
        st.write(f'{cat_var_str}（{xcat_var_d}）によって、')

        for num_var in num_vars:
            st.write(f'● {num_var}')

        st.write("これらの数値変数に有意な差が生まれるか検定します。")

        # グラフタイトルを表示するチェックボックス
        show_graph_title = st.checkbox('グラフタイトルを表示する', value=True)  # デフォルトでチェックされている

        # 分散分析の実行
        if st.button('分散分析の実行'):
            st.subheader('【分析結果】')
            st.write('【要約統計量】')

            # 要約統計量の計算
            summaryColumns = ["有効N", "平均値", "中央値", "標準偏差", "分散", "最小値", "最大値"]
            df_summary = pd.DataFrame(index=num_vars, columns=summaryColumns)

            for num_var in num_vars:
                y = df[num_var]
                df_summary.at[num_var, '有効N'] = len(y)
                df_summary.at[num_var, '平均値'] = y.mean()
                df_summary.at[num_var, '中央値'] = median(y)
                df_summary.at[num_var, '標準偏差'] = y.std(ddof=1)
                df_summary.at[num_var, '分散'] = variance(y)
                df_summary.at[num_var, '最小値'] = y.min()
                df_summary.at[num_var, '最大値'] = y.max()

            # 要約統計量の表示
            st.write(df_summary.style.format("{:.2f}"))

            st.write('【分散分析（対応なし）】')

            # 結果を保存するデータフレームの初期化
            groups = df[cat_var_str].unique()
            k = len(groups)
            N = len(df)
            columns = ['全体M', '全体S.D'] + \
                [f'{group}M' for group in groups] + \
                [f'{group}S.D' for group in groups] + \
                ['群間自由度', '群内自由度', 'F', 'p', 'sign', 'η²', 'ω²']
            df_results = pd.DataFrame(columns=columns, index=num_vars)

            for num_var in num_vars:
                group_data = [df[df[cat_var_str] == group][num_var] for group in groups]
                overall_mean = df[num_var].mean()
                overall_std = df[num_var].std(ddof=1)
                fval, pval = stats.f_oneway(*group_data)

                # 自由度の計算
                df_between = k - 1  # 群間自由度
                df_within = N - k     # 群内自由度

                # 分散と効果量の計算
                ss_between = sum([len(group) * (group.mean() - overall_mean)**2 for group in group_data])
                ss_total = sum((df[num_var] - overall_mean)**2)
                ss_within = ss_total - ss_between
                ms_within = ss_within / df_within

                eta_squared = ss_between / ss_total
                omega_squared = (ss_between - (df_between * ms_within)) / (ss_total + ms_within)

                means = [group.mean() for group in group_data]
                stds = [group.std(ddof=1) for group in group_data]

                if pval < 0.01:
                    sign = '**'
                elif pval < 0.05:
                    sign = '*'
                elif pval < 0.1:
                    sign = '†'
                else:
                    sign = 'n.s.'

                df_results.loc[num_var] = [overall_mean, overall_std] + means + stds + \
                    [df_between, df_within, fval, pval, sign, eta_squared, omega_squared]

            # 結果の表示
            numeric_columns = df_results.select_dtypes(include=['float64', 'int64']).columns
            styled_df = df_results.style.format({col: "{:.2f}" for col in numeric_columns})
            st.write(styled_df)

            st.write("【多重比較の結果】")

            for num_var in num_vars:
                # TukeyのHSDテストを実行
                try:
                    tukey_result = pairwise_tukeyhsd(df[num_var], df[cat_var_str])
                    # 結果をデータフレームに変換
                    tukey_df = pd.DataFrame(data=tukey_result._results_table.data[1:], 
                                            columns=tukey_result._results_table.data[0])
                    st.write(f'＜　　{num_var}　　に対する多重比較の結果＞')
                    st.write(tukey_df)

                    # sign_captionを初期化
                    sign_caption = ''

                    # 各記号に対するチェックを実行
                    for p_adj in tukey_df['p-adj']:
                        if p_adj < 0.01 and 'p<0.01**' not in sign_caption:
                            sign_caption += 'p<0.01** '
                        elif p_adj < 0.05 and 'p<0.05*' not in sign_caption:
                            sign_caption += 'p<0.05* '
                        elif p_adj < 0.1 and 'p<0.1†' not in sign_caption:
                            sign_caption += 'p<0.1† '
                    st.caption(sign_caption)
                except Exception as e:
                    st.error(f"TukeyのHSDテスト実行中にエラーが発生しました: {e}")

            # サンプルサイズの表示
            st.write('＜サンプルサイズ＞')
            st.write(f'全体N ＝ {len(df)}')
            for group_name in groups:
                st.write(f'● {group_name}： {len(df[df[cat_var_str] == group_name])}')

            st.subheader('【解釈の補助】')

            for index, row in df_results.iterrows():
                sign = row['sign']
                if sign in ['**', '*']:
                    significance = "有意な差が生まれる"
                elif sign == '†':
                    significance = "有意な差が生まれる傾向にある"
                else:
                    significance = "有意な差が生まれない"
                p_value = row['p']
                st.write(f'{cat_var_str}によって、【{index}】には{significance}')
                st.write(f'（ p = {p_value:.2f} ）')

            st.subheader('【可視化】')

            # ブラケット付きの棒グラフを描画する関数
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

            # レベル割り当て関数（比較が重ならないようレベルを決定）
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
                            # 完全に分離されている場合のみ配置可能
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

            for num_var in num_vars:
                # TukeyのHSDテストを実行
                try:
                    tukey_result = pairwise_tukeyhsd(df[num_var], df[cat_var_str])
                    # 結果をデータフレームに変換
                    tukey_df = pd.DataFrame(data=tukey_result._results_table.data[1:], 
                                            columns=tukey_result._results_table.data[0])
                except Exception as e:
                    st.error(f"TukeyのHSDテスト実行中にエラーが発生しました: {e}")
                    continue

                # 有意な比較を抽出
                significant_comparisons = []
                for _, row in tukey_df.iterrows():
                    group1 = row['group1']
                    group2 = row['group2']
                    p_value = row['p-adj']
                    if p_value < 0.1:
                        if p_value < 0.01:
                            significance = '**'
                        elif p_value < 0.05:
                            significance = '*'
                        else:
                            significance = '†'
                        significant_comparisons.append((group1, group2, p_value, significance))

                # 群ごとの平均値と標準誤差を計算
                group_means = df.groupby(cat_var_str)[num_var].mean()
                group_errors = df.groupby(cat_var_str)[num_var].std(ddof=1) / np.sqrt(df.groupby(cat_var_str)[num_var].count())

                # カテゴリを数値にマッピング
                category_positions = {group: i for i, group in enumerate(group_means.index)}
                
                # レベルを割り当て
                comparisons = [(comp[0], comp[1]) for comp in significant_comparisons]
                comparison_levels, num_levels = assign_levels(comparisons, category_positions) if comparisons else ([], 0)
                x_values = [category_positions[group] for group in group_means.index]

                fig = go.Figure()

                fig.add_trace(go.Bar(
                    x=x_values,
                    y=group_means.values,
                    error_y=dict(type='data', array=group_errors.values, visible=True),
                    marker_color='skyblue'
                ))

                # x軸をカテゴリ名で表示
                fig.update_xaxes(
                    tickvals=list(category_positions.values()),
                    ticktext=list(category_positions.keys())
                )

                if show_graph_title:
                    fig.update_layout(title_text=f'{num_var} by {cat_var_str}')

                # y軸の最大値を計算（群の数とレベル数に応じて動的に調整）
                base_y_max = max(group_means + group_errors) * 1.1 if not group_means.empty else 1
                num_groups = len(group_means)

                # オフセットとステップサイズを群数とレベル数に応じて調整
                y_offset = base_y_max * max(0.06, 0.15 / num_groups)  # 群が多いほど相対的に小さく
                step_size = base_y_max * max(0.10, 0.25 / num_groups)  # 群が多いほど相対的に小さく

                # レベル数が多い場合はさらに調整
                if num_levels > 3:
                    step_size = step_size * (1 + (num_levels - 3) * 0.1)

                # レベルごとに必要な余白を計算
                additional_height = num_levels * step_size + y_offset * 2.5
                y_max = base_y_max + additional_height

                # アノテーション配置の調整係数（群数に応じて動的に調整）
                vline_bottom_factor = max(0.3, 0.8 / num_groups)  # ブラケット下端の余白
                bracket_offset_factor = max(0.2, 0.5 / num_groups)  # ブラケット上端の追加余白
                annotation_offset_factor = max(0.3, 0.8 / num_groups)  # アノテーションの余白

                # ブラケットとアノテーションを追加
                for idx, (comp, level) in enumerate(zip(significant_comparisons, comparison_levels)):
                    group1, group2, p_value, significance = comp
                    x0 = category_positions[group1]
                    x1 = category_positions[group2]

                    # ブラケットの下端はエラーバーの上端 + 余白
                    y_vline_bottom = max(group_means[group1] + group_errors[group1],
                                         group_means[group2] + group_errors[group2]) + y_offset * vline_bottom_factor

                    # ブラケットの上端はレベルに応じて設定
                    bracket_y = y_vline_bottom + (level * step_size) + y_offset * bracket_offset_factor

                    # ブラケットを追加
                    fig.add_shape(create_bracket_shape(x0, x1, y_vline_bottom, bracket_y))

                    # アノテーションを追加（ブラケットの上に十分な余白を確保）
                    annotation_y = bracket_y + y_offset * annotation_offset_factor
                    fig.add_annotation(create_bracket_annotation(x0, x1, annotation_y, f'p < {p_value:.2f} {significance}'))

                # y軸の範囲を設定（上部に余裕を持たせる）
                fig.update_yaxes(range=[0, y_max * 1.05])

                # 日本語フォントの設定
                fig.update_layout(font=dict(family="IPAexGothic"))

                st.plotly_chart(fig, use_container_width=True)

                # Excelダウンロードボタン
                excel_data = common.export_plotly_to_excel(fig, filename=f"一要因分散分析_{y_column}.xlsx", sheet_name="グラフ")
                st.download_button(
                    label="📊 グラフをExcelでダウンロード",
                    data=excel_data,
                    file_name=f"一要因分散分析_{y_column}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # グラフキャプションの追加
                caption_text = f"グループごとの平均値 (SE): "
                caption_text += ", ".join([f"{group}: {mean:.2f} ({error:.2f})" for group, mean, error in 
                                           zip(group_means.index, group_means.values, group_errors.values)])
                caption_text += f", F = {df_results.loc[num_var, 'F']:.2f}, p = {df_results.loc[num_var, 'p']:.3f}, η² = {df_results.loc[num_var, 'η²']:.2f}, ω² = {df_results.loc[num_var, 'ω²']:.2f}"
                st.caption(caption_text)

# フッター
common.display_copyright()
common.display_special_thanks()
