import numpy as np
import pandas as pd
import pingouin as pg
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from statsmodels.stats.multicomp import pairwise_tukeyhsd

import common


st.set_page_config(page_title="二要因混合分散分析", layout="wide")

st.title("二要因混合分散分析")
common.display_header()
st.write("被験者内因子（前測・後測）と、被験者間因子（１つのみ）を用いた混合ANOVAを実行します。")

# 分析イメージ（画像ファイルがある場合）
try:
    image = Image.open('images/anova_mixed.png')
    st.image(image)
except Exception as e:
    st.warning("画像ファイルが見つかりません。")

# ファイルアップローダー
uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])
use_demo_data = st.checkbox('デモデータを使用')

# データ読み込み
df = None
if use_demo_data:
    try:
        df = pd.read_excel('datasets/2way_anova_demo_mix.xlsx', sheet_name=0)
        st.write(df.head())
    except FileNotFoundError:
        st.error("デモデータファイルが見つかりません。パスを確認してください。")
else:
    if uploaded_file is not None:
        try:
            if uploaded_file.type == 'text/csv':
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.write(df.head())
        except Exception as e:
            st.error(f"ファイル読み込み中にエラーが発生しました: {e}")

# p値の解釈用関数
def interpret_p(p):
    if p < 0.01:
        return "有意な差が認められる", "**"
    elif p < 0.05:
        return "有意な差が認められる", "*"
    elif p < 0.1:
        return "有意な差が認められる傾向にある", "†"
    else:
        return "有意な差は認められない", "n.s."

# ブラケット・アノテーション追加用の関数
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
        path=f'M {x0},{y_vline_bottom} L {x0},{bracket_y} L {x1},{bracket_y} L {x1},{y_vline_bottom}',
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
        pos1 = cat_positions.get(comp[0], -1)
        pos2 = cat_positions.get(comp[1], -1)
        if pos1 == -1 or pos2 == -1:
            continue  # カテゴリが見つからない場合はスキップ
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

if df is not None:
    st.subheader("【変数の選択】")
    all_cols = df.columns.tolist()
    
    # 被験者IDの選択（必須）
    subject_col = st.selectbox("被験者IDの列を選択してください (必須)", all_cols, index=0)
    
    # 被験者間因子は候補一覧から１つ必ず選択
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    if not categorical_cols:
        st.error("被験者間因子として利用できるカテゴリ変数が存在しません。")
    else:
        selected_between = st.selectbox("被験者間因子（対応なし）を選択してください（１つのみ選択）", categorical_cols)
    
    # 被験者内因子（対応あり）の選択：観測変数（前測）と測定変数（後測）のペアを選択
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    st.subheader("被験者内因子の選択")
    st.write("【観測変数】（前測）と【測定変数】（後測）のペアを選択してください。")
    pre_vars = st.multiselect("観測変数を選択してください", numerical_cols, key="pre_vars")
    remaining_cols = [col for col in numerical_cols if col not in pre_vars]
    post_vars = st.multiselect("測定変数を選択してください", remaining_cols, key="post_vars")
    
    if len(pre_vars) != len(post_vars):
        st.error("観測変数と測定変数の数は同じでなければなりません。")
    elif not pre_vars or not post_vars:
        st.error("観測変数と測定変数を選択してください。")
    else:
        st.success("分析可能な変数が選択されました。")
        st.subheader("分析前の確認")
        for pre, post in zip(pre_vars, post_vars):
            st.write(f"● {pre} → {post}")
        st.write("これらの変数に前後の差があるか検定します。")
        
        final_tables = []
        
        # 各変数ペアごとに処理
        for i, (pre, post) in enumerate(zip(pre_vars, post_vars)):
            st.markdown(f"## 分析対象変数ペア {i+1}: {pre}（前測） と {post}（後測）")
            
            # ワイド→ロング変換
            n = len(df)
            df_long = pd.DataFrame()
            df_long[subject_col] = np.repeat(df[subject_col].values, 2)
            df_long[selected_between] = np.repeat(df[selected_between].values, 2)
            df_long["Time"] = ["前", "後"] * n
            df_long["value"] = np.concatenate([df[pre].values, df[post].values])
            
            st.write("【セルごとの要約統計量】")
            desc = df_long.groupby([selected_between, "Time"])["value"].agg(["count", "mean", "std", "min", "max"]).reset_index()
            st.write(desc.style.format({"mean": "{:.2f}", "std": "{:.2f}", "min": "{:.2f}", "max": "{:.2f}"}))
            
            st.write("【混合ANOVAの実行】")
            try:
                aov = pg.mixed_anova(dv="value", within="Time", between=selected_between, subject=subject_col, data=df_long)
                st.write(aov)
            except Exception as e:
                st.error(f"混合ANOVA実行中にエラーが発生しました: {e}")
                continue
            
            st.write("【多重比較（Tukey HSDテスト）】")
            df_long["Interaction"] = df_long[selected_between].astype(str) + "_" + df_long["Time"]
            try:
                tukey = pairwise_tukeyhsd(endog=df_long["value"], groups=df_long["Interaction"])
                tukey_df = pd.DataFrame(data=tukey._results_table.data[1:],
                                        columns=tukey._results_table.data[0])
                st.write(tukey_df)
            except Exception as e:
                st.error(f"Tukey HSDテスト実行中にエラーが発生しました: {e}")
                continue
            
            st.subheader("【多重比較の解釈】")
            for idx, row in tukey_df.iterrows():
                group1 = row["group1"]
                group2 = row["group2"]
                p_val = row["p-adj"]
                interp_text, sig = interpret_p(p_val)
                st.write(f"【{group1} vs {group2}】 → {interp_text} (p = {p_val:.3f} {sig})")
            
            st.subheader("【可視化】")
            # 前測・後測をまとめたグラフ
            df_group = df_long.groupby([selected_between, "Time"]).agg(
                count=("value", "count"),
                mean=("value", "mean"),
                std=("value", "std")
            ).reset_index()
            df_group["se"] = df_group["std"] / np.sqrt(df_group["count"])
            levels = sorted(df_group[selected_between].unique())
            delta = 0.2
            category_positions = {grp: i for i, grp in enumerate(levels)}
            x_values = [category_positions[grp] for grp in levels]
            # 前測は左にずらし、後測は右にずらす
            x_pre = [x - delta for x in x_values]
            x_post = [x + delta for x in x_values]
            pre_stats = df_group[df_group["Time"]=="前"].set_index(selected_between)
            post_stats = df_group[df_group["Time"]=="後"].set_index(selected_between)
            pre_means = [pre_stats.loc[grp, "mean"] if grp in pre_stats.index else 0 for grp in levels]
            pre_err = [pre_stats.loc[grp, "se"] if grp in pre_stats.index else 0 for grp in levels]
            post_means = [post_stats.loc[grp, "mean"] if grp in post_stats.index else 0 for grp in levels]
            post_err = [post_stats.loc[grp, "se"] if grp in post_stats.index else 0 for grp in levels]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=x_pre,
                y=pre_means,
                error_y=dict(type="data", array=pre_err, visible=True),
                name="前測",
                marker_color="skyblue"
            ))
            fig.add_trace(go.Bar(
                x=x_post,
                y=post_means,
                error_y=dict(type="data", array=post_err, visible=True),
                name="後測",
                marker_color="lightgreen"
            ))
            fig.update_xaxes(
                tickvals=x_values,
                ticktext=levels
            )
            
            # 各条件ごとに Tukey HSD を実施して、ブラケットとアノテーションを追加（前測）
            try:
                tukey_pre = pairwise_tukeyhsd(endog=df_long[df_long["Time"]=="前"]["value"],
                                              groups=df_long[df_long["Time"]=="前"][selected_between])
                tukey_pre_df = pd.DataFrame(data=tukey_pre._results_table.data[1:],
                                            columns=tukey_pre._results_table.data[0])
            except Exception as e:
                st.error(f"Tukey HSDテスト（前測）実行中にエラーが発生しました: {e}")
                tukey_pre_df = pd.DataFrame()
            significant_comparisons_pre = []
            for _, row in tukey_pre_df.iterrows():
                grp1 = row['group1']
                grp2 = row['group2']
                p_value = row['p-adj']
                if p_value < 0.1:
                    if p_value < 0.01:
                        significance = '**'
                    elif p_value < 0.05:
                        significance = '*'
                    else:
                        significance = '†'
                    significant_comparisons_pre.append((grp1, grp2, p_value, significance))
            comp_levels_pre, num_levels_pre = assign_levels(significant_comparisons_pre, category_positions) if significant_comparisons_pre else ([], 0)
            
            # 後測の比較
            try:
                tukey_post = pairwise_tukeyhsd(endog=df_long[df_long["Time"]=="後"]["value"],
                                               groups=df_long[df_long["Time"]=="後"][selected_between])
                tukey_post_df = pd.DataFrame(data=tukey_post._results_table.data[1:],
                                             columns=tukey_post._results_table.data[0])
            except Exception as e:
                st.error(f"Tukey HSDテスト（後測）実行中にエラーが発生しました: {e}")
                tukey_post_df = pd.DataFrame()
            significant_comparisons_post = []
            for _, row in tukey_post_df.iterrows():
                grp1 = row['group1']
                grp2 = row['group2']
                p_value = row['p-adj']
                if p_value < 0.1:
                    if p_value < 0.01:
                        significance = '**'
                    elif p_value < 0.05:
                        significance = '*'
                    else:
                        significance = '†'
                    significant_comparisons_post.append((grp1, grp2, p_value, significance))
            comp_levels_post, num_levels_post = assign_levels(significant_comparisons_post, category_positions) if significant_comparisons_post else ([], 0)
            
            base_y_max = max(max(np.array(pre_means) + np.array(pre_err)),
                             max(np.array(post_means) + np.array(post_err))) * 1.1
            num_groups = len(levels)

            # オフセットとステップサイズを群数とレベル数に応じて調整
            y_offset = base_y_max * max(0.06, 0.15 / num_groups)  # 群が多いほど相対的に小さく
            step_size = base_y_max * max(0.10, 0.25 / num_groups)  # 群が多いほど相対的に小さく

            # レベル数が多い場合はさらに調整
            max_num_levels = max(num_levels_pre, num_levels_post)
            if max_num_levels > 3:
                step_size = step_size * (1 + (max_num_levels - 3) * 0.1)

            # アノテーション配置の調整係数（群数に応じて動的に調整）
            vline_bottom_factor = max(0.3, 0.8 / num_groups)  # ブラケット下端の余白
            bracket_offset_factor = max(0.2, 0.5 / num_groups)  # ブラケット上端の追加余白
            annotation_offset_factor = max(0.3, 0.8 / num_groups)  # アノテーションの余白

            # 前測のブラケット・アノテーション
            for idx, (comp, level) in enumerate(zip(significant_comparisons_pre, comp_levels_pre)):
                grp1, grp2, p_value, significance = comp
                if grp1 in category_positions and grp2 in category_positions:
                    x0 = category_positions[grp1] - delta
                    x1 = category_positions[grp2] - delta
                    y_vline_bottom = max(pre_means[levels.index(grp1)] + pre_err[levels.index(grp1)],
                                         pre_means[levels.index(grp2)] + pre_err[levels.index(grp2)]) + y_offset * vline_bottom_factor
                    bracket_y = y_vline_bottom + (level * step_size) + y_offset * bracket_offset_factor
                    fig.add_shape(create_bracket_shape(x0, x1, y_vline_bottom, bracket_y))
                    annotation_y = bracket_y + y_offset * annotation_offset_factor
                    fig.add_annotation(create_bracket_annotation(x0, x1, annotation_y, f'p < {p_value:.2f} {significance}'))

            # 後測のブラケット・アノテーション
            for idx, (comp, level) in enumerate(zip(significant_comparisons_post, comp_levels_post)):
                grp1, grp2, p_value, significance = comp
                if grp1 in category_positions and grp2 in category_positions:
                    x0 = category_positions[grp1] + delta
                    x1 = category_positions[grp2] + delta
                    y_vline_bottom = max(post_means[levels.index(grp1)] + post_err[levels.index(grp1)],
                                         post_means[levels.index(grp2)] + post_err[levels.index(grp2)]) + y_offset * vline_bottom_factor
                    bracket_y = y_vline_bottom + (level * step_size) + y_offset * bracket_offset_factor
                    fig.add_shape(create_bracket_shape(x0, x1, y_vline_bottom, bracket_y))
                    annotation_y = bracket_y + y_offset * annotation_offset_factor
                    fig.add_annotation(create_bracket_annotation(x0, x1, annotation_y, f'p < {p_value:.2f} {significance}'))
            
            fig.update_yaxes(range=[0, base_y_max + (max_num_levels * step_size) + y_offset * 2.5])
            fig.update_layout(font=dict(family="IPAexGothic"), barmode="group", title_text=f"{pre}・{post} の 前後まとめた結果")
            st.plotly_chart(fig, use_container_width=True)

            # Excelダウンロードリンク
            excel_data = common.export_plotly_to_excel(fig, filename=f"二要因混合分散分析_{pre}_{post}.xlsx", sheet_name="グラフ")
            import base64
            b64 = base64.b64encode(excel_data).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="二要因混合分散分析_{pre}_{post}.xlsx">📊 グラフをExcelでダウンロード</a>'
            st.markdown(href, unsafe_allow_html=True)

            # 各群の平均値 (SD) を計算（全ての時間点の値の平均を使用）
            group_summary = df_long.groupby(selected_between)["value"].agg(['mean', 'std', 'count']).reset_index()
            group_summary['se'] = group_summary['std'] / np.sqrt(group_summary['count'])
            group_means = dict(zip(group_summary[selected_between], group_summary['mean']))
            group_errors = dict(zip(group_summary[selected_between], group_summary['se']))
            caption_text = "各群の平均値 (SE): " + ", ".join([
                f"{grp}: {group_means[grp]:.2f} ({group_errors[grp]:.2f})" for grp in sorted(levels)
            ])
            st.caption(caption_text)
            
            # ⑥ 各従属変数の全体結果のまとめテーブル作成（ピボット形式）
            summary = df_long.groupby([selected_between, "Time"]).agg(
                mean=("value", "mean"),
                std=("value", "std")
            ).reset_index()
            pivot_df = summary.pivot(index=selected_between, columns="Time", values=["mean", "std"])
            pivot_df.columns = [f"{col[1]}_{'M' if col[0]=='mean' else 'S.D'}" for col in pivot_df.columns]
            pivot_df = pivot_df.reset_index()
            pivot_df.insert(0, "変数", pre)
            # ANOVA結果から効果の記号を抽出（存在しなければ "n.s."）
            if not aov[aov["Source"]=="Between"].empty:
                p_between_val = aov.loc[aov["Source"]=="Between", "p-unc"].values[0]
                _, sig_between = interpret_p(p_between_val)
            else:
                sig_between = "n.s."
            if not aov[aov["Source"]=="Time"].empty:
                p_time_val = aov.loc[aov["Source"]=="Time", "p-unc"].values[0]
                _, sig_time = interpret_p(p_time_val)
            else:
                sig_time = "n.s."
            if not aov[aov["Source"]=="Interaction"].empty:
                p_interaction_val = aov.loc[aov["Source"]=="Interaction", "p-unc"].values[0]
                _, sig_interaction = interpret_p(p_interaction_val)
            else:
                sig_interaction = "n.s."
            pivot_df[f"{selected_between}の主効果"] = ""
            pivot_df["前後の主効果"] = ""
            pivot_df["交互作用"] = ""
            pivot_df.loc[pivot_df.index[0], f"{selected_between}の主効果"] = sig_between
            pivot_df.loc[pivot_df.index[0], "前後の主効果"] = sig_time
            pivot_df.loc[pivot_df.index[0], "交互作用"] = sig_interaction
            # 数値を小数点第2位まで表示するために文字列に変換（例: 5.0 -> "5.00"）
            pivot_df = pivot_df.applymap(lambda x: "{:.2f}".format(x) if isinstance(x, (int, float)) else x)
            final_tables.append(pivot_df)
        
        # 全従属変数のまとめ（連結して表示）
        if final_tables:
            st.subheader("【全体結果のまとめ】")
            all_final = pd.concat(final_tables, ignore_index=True)
            st.dataframe(all_final)
            st.caption("p<0.1†   p<0.05*   p<0.01**")
        
        common.display_copyright()
        common.display_special_thanks()
