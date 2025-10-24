import numpy as np
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import statsmodels.formula.api as smf
import streamlit as st
from PIL import Image
from statsmodels.stats.multicomp import pairwise_tukeyhsd

import common


st.set_page_config(page_title="二要因分散分析(対応なし)", layout="wide")

st.title("二要因分散分析(対応なし)")
common.display_header()
st.write("2つの独立変数（因子）と1つ以上の従属変数を用いて、二要因分散分析（主効果・交互作用効果）を実施します。")
st.write("")

# 分析イメージ（画像ファイルがある場合）
try:
    image = Image.open('images/anova_two_way.png')
    st.image(image)
except Exception as e:
    st.warning("画像ファイルが見つかりません。")

# ファイルアップローダー
uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])
use_demo_data = st.checkbox('デモデータを使用')

# データの読み込み
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

# mark_significance 関数の定義
def mark_significance(p):
    if p < 0.01:
        return '**'
    elif p < 0.05:
        return '*'
    elif p < 0.1:
        return '†'
    else:
        return 'n.s.'

# 二要因分散分析の設定
if df is not None:
    st.subheader("【変数の選択】")
    # 独立変数（因子）は文字列型・カテゴリ型から選択
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    # 従属変数は数値型から選択
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    st.write("※ 二要因分散分析では、2つの独立変数（因子）と1つ以上の従属変数を選択してください。")
    factor_vars = st.multiselect('独立変数（因子）を選択してください', categorical_cols, max_selections=2)
    dep_vars = st.multiselect('従属変数（数値変数）を選択してください', numerical_cols)
    
    if len(factor_vars) != 2:
        st.error("2つの独立変数（因子）を選択してください。")
    elif not dep_vars:
        st.error("少なくとも1つの従属変数を選択してください。")
    else:
        factor1 = factor_vars[0]
        factor2 = factor_vars[1]
        if len(df[factor1].unique()) < 2 or len(df[factor2].unique()) < 2:
            st.error("各独立変数は少なくとも2つのレベルが必要です。")
        else:
            st.success("分析可能な変数が選択されました。")
            st.subheader("【分析前の確認】")
            st.write(f"独立変数1: **{factor1}** (レベル: {list(df[factor1].unique())})")
            st.write(f"独立変数2: **{factor2}** (レベル: {list(df[factor2].unique())})")
            st.write(f"従属変数: **{', '.join(dep_vars)}**")
            
            # 各従属変数ごとの最終結果テーブルを保存するリスト
            final_tables = []
            
            # p値の記号変換用関数（別名 interpret_p として利用可能）
            def interpret_p(p):
                if p < 0.01:
                    return "**"
                elif p < 0.05:
                    return "*"
                elif p < 0.1:
                    return "†"
                else:
                    return "n.s."
            
            # 各従属変数について解析
            for dv in dep_vars:
                st.markdown(f"## 従属変数: {dv}")
                
                # ① セルごとの要約統計量（因子1 × 因子2 の組み合わせ）
                st.write("【セルごとの要約統計量】")
                df_summary = df.groupby([factor1, factor2])[dv].agg(
                    サンプル数='count',
                    平均値='mean',
                    中央値='median',
                    標準偏差=lambda x: x.std(ddof=1),
                    分散=lambda x: x.var(ddof=1),
                    最小値='min',
                    最大値='max'
                ).reset_index()
                st.write(df_summary.style.format({
                    "平均値": "{:.2f}",
                    "標準偏差": "{:.2f}",
                    "中央値": "{:.2f}",
                    "分散": "{:.2f}",
                    "最小値": "{:.2f}",
                    "最大値": "{:.2f}"
                }))
                
                # ② 二要因分散分析の実行
                st.write("【二要因分散分析の実行】")
                try:
                    formula = f'Q("{dv}") ~ C(Q("{factor1}")) * C(Q("{factor2}"))'
                    model = smf.ols(formula, data=df).fit()
                    anova_results = sm.stats.anova_lm(model, typ=2)
                    st.write(anova_results.style.format("{:.2f}"))
                except Exception as e:
                    st.error(f"二要因分散分析実行中にエラーが発生しました: {e}")
                    continue
                
                # ③ ANOVA結果から解釈の補助を表示
                st.subheader("【解釈の補助】")
                df_anova = anova_results.copy()
                df_anova['sign'] = df_anova['PR(>F)'].apply(mark_significance)
                for effect in df_anova.index:
                    if effect == 'Residual':
                        continue
                    p_value = df_anova.loc[effect, 'PR(>F)']
                    sign = df_anova.loc[effect, 'sign']
                    if sign in ['**', '*']:
                        interpretation = "有意な差が認められる"
                    elif sign == '†':
                        interpretation = "有意な差が認められる傾向にある"
                    else:
                        interpretation = "有意な差は認められない"
                    st.write(f"【{effect}】 → {interpretation}（p = {p_value:.3f}）")
                
                # ④ 多重比較：TukeyのHSDテスト
                st.write("【多重比較（TukeyのHSDテスト）】")
                # Interaction列を作成（因子の組み合わせ）
                df['Interaction'] = df[factor1].astype(str) + "_" + df[factor2].astype(str)
                try:
                    tukey_result = pairwise_tukeyhsd(endog=df[dv], groups=df['Interaction'])
                    tukey_df = pd.DataFrame(
                        data=tukey_result._results_table.data[1:],
                        columns=tukey_result._results_table.data[0]
                    )
                    st.write(tukey_df.style.format({
                        'meandiff': '{:.2f}',
                        'p-adj': '{:.2f}',
                        'lower': '{:.2f}',
                        'upper': '{:.2f}'
                    }))
                    # 有意性のキャプション
                    sign_caption = ''
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
                
                # ⑤ 可視化：Interactionごとの棒グラフの作成
                st.subheader("【可視化】")
                # ※ここでは、単純に元のdfのコピーを用いてグループごとの平均・標準誤差を計算
                df_long = df.copy()
                group_means = df_long.groupby('Interaction')[dv].mean()
                group_errors = df_long.groupby('Interaction')[dv].apply(lambda x: x.std(ddof=1) / np.sqrt(len(x)))
                sorted_groups = sorted(group_means.index)
                category_positions = {grp: i for i, grp in enumerate(sorted_groups)}
                x_values = [category_positions[grp] for grp in sorted_groups]
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=x_values,
                    y=[group_means[grp] for grp in sorted_groups],
                    error_y=dict(type='data', array=[group_errors[grp] for grp in sorted_groups], visible=True),
                    marker_color='skyblue'
                ))
                fig.update_xaxes(
                    tickvals=list(category_positions.values()),
                    ticktext=list(category_positions.keys())
                )
                fig.update_layout(title_text=f"{dv} by Interaction ( {factor1} x {factor2} )",
                                  xaxis_title="Interaction",
                                  yaxis_title=dv)
                st.plotly_chart(fig, use_container_width=True)

                # Excelダウンロードボタン
                excel_data = common.export_plotly_to_excel(fig, filename=f"二要因分散分析_{dv}.xlsx", sheet_name="グラフ")
                st.download_button(
                    label="📊 グラフをExcelでダウンロード",
                    data=excel_data,
                    file_name=f"二要因分散分析_{dv}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # ⑥ Final Table（全体結果のまとめ）の作成（ピボット形式）
                st.subheader("【全体結果のまとめ（Final Table）】")
                # 各セル（因子1と因子2の組み合わせ）の平均値と標準偏差を集計
                cell_summary = df.groupby([factor1, factor2])[dv].agg(
                    平均値='mean',
                    標準偏差=lambda x: x.std(ddof=1),
                    サンプル数='count'
                ).reset_index()
                # Mean (SD)形式の文字列を作成
                cell_summary['Mean (SD)'] = cell_summary.apply(
                    lambda row: f"{row['平均値']:.2f} ({row['標準偏差']:.2f})", axis=1
                )
                # ピボットテーブルとして整形（行：factor1、列：factor2）
                pivot_df = cell_summary.pivot(index=factor1, columns=factor2, values='Mean (SD)').reset_index()
                # 最初の列として、従属変数名を示す "変数" 列を追加
                pivot_df.insert(0, "変数", dv)
                
                # ANOVA結果から各効果の有意性を抽出
                effect_names = {
                    "factor1": f'C(Q("{factor1}"))',
                    "factor2": f'C(Q("{factor2}"))',
                    "interaction": f'C(Q("{factor1}")):C(Q("{factor2}"))'
                }
                sig_factor1 = interpret_p(anova_results.loc[effect_names["factor1"], 'PR(>F)']) if effect_names["factor1"] in anova_results.index else "n.s."
                sig_factor2 = interpret_p(anova_results.loc[effect_names["factor2"], 'PR(>F)']) if effect_names["factor2"] in anova_results.index else "n.s."
                sig_interaction = interpret_p(anova_results.loc[effect_names["interaction"], 'PR(>F)']) if effect_names["interaction"] in anova_results.index else "n.s."
                
                # 有意性を示す列を追加（1行目に記載）
                pivot_df[f"{factor1}の主効果"] = ""
                pivot_df[f"{factor2}の主効果"] = ""
                pivot_df["交互作用"] = ""
                pivot_df.loc[pivot_df.index[0], f"{factor1}の主効果"] = sig_factor1
                pivot_df.loc[pivot_df.index[0], f"{factor2}の主効果"] = sig_factor2
                pivot_df.loc[pivot_df.index[0], "交互作用"] = sig_interaction
                
                st.dataframe(pivot_df)
                final_tables.append(pivot_df)
            
            # 全従属変数のまとめ（連結して表示）
            if final_tables:
                st.subheader("【全体結果のまとめ】")
                all_final = pd.concat(final_tables, ignore_index=True)
                st.dataframe(all_final)
                st.caption("p<0.1†   p<0.05*   p<0.01**")
            
            common.display_copyright()
            common.display_special_thanks()
