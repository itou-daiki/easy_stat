import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from statistics import median, variance
from PIL import Image
import plotly.graph_objects as go
import common

st.set_page_config(page_title="t検定(対応なし)", layout="wide")

st.title("t検定(対応なし)")
common.display_header()
st.write("変数の選択　→　t検定　→　表作成　→　解釈の補助を行います")
st.write("")

# 分析のイメージ
image = Image.open('images/ttest.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('datasets/ttest_demo.xlsx', sheet_name=0)
    st.write(df.head())
else:
    if uploaded_file is not None:
        if uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
            st.write(df.head())
        else:
            df = pd.read_excel(uploaded_file)
            st.write(df.head())

if df is not None:
    # カテゴリ変数の抽出
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    # 数値変数の抽出
    numerical_cols = df.select_dtypes(exclude=['object', 'category']).columns.tolist()

    # カテゴリ変数の選択
    st.subheader("カテゴリ変数の選択")
    cat_var = st.multiselect('カテゴリ変数（独立変数）を選択してください', categorical_cols, max_selections=1)

    # 数値変数の選択
    st.subheader("数値変数の選択")
    num_vars = st.multiselect('数値変数（従属変数）を選択してください', numerical_cols)

    # エラー処理
    if not cat_var:
        st.error("カテゴリ変数を選択してください。")
    elif not num_vars:
        st.error("数値変数を選択してください。")
    elif len(df[cat_var].iloc[:, 0].unique()) != 2:
        st.error("独立変数が2群になっていないため、分析を実行できません")
    else:
        st.success("分析可能な変数を選択しました。分析を実行します。")

        # 独立変数から重複のないデータを抽出し、リストに変換
        xcat_var_d = df[cat_var].iloc[:, 0].unique().tolist()
        st.subheader('【分析前の確認】')
        cat_var_str = str(cat_var[0])
        st.write(f'{cat_var_str}（{xcat_var_d[0]}・{xcat_var_d[1]}）によって、')

        for num_var in num_vars:
            st.write(f'● {num_var}')

        st.write("これらの数値変数に有意な差が生まれるか検定します。")

        # グラフタイトルを表示するチェックボックス
        show_graph_title = st.checkbox('グラフタイトルを表示する', value=True)  # デフォルトでチェックされている

        # t検定の実行
        if st.button('t検定の実行'):
            st.subheader('【分析結果】')
            st.write('【要約統計量】')

            # 数値変数の要素の数を取得
            num_range = len(num_vars)

            # 各値の初期化
            n = 1
            summaryList = num_vars
            summaryColumns = ["有効N", "平均値", "中央値", "標準偏差", "分散",
                              "最小値", "最大値"]

            # 目的変数、従属変数から作業用データフレームのセット
            df00_list = cat_var + num_vars
            df00 = df[df00_list]

            # サマリ(df0)用のデータフレームのセット
            df0 = pd.DataFrame(index=summaryList, columns=summaryColumns)

            # サマリ(df0)用のデータフレームに平均値と標準偏差を追加
            for summary in range(num_range):
                # 列データの取得（nは従属変数の配列番号）
                y = df00.iloc[:, n]

                # 従属変数の列データの計算処理
                df0.at[df00.columns[n], '有効N'] = len(y)
                df0.at[df00.columns[n], '平均値'] = y.mean()
                df0.at[df00.columns[n], '中央値'] = median(y)
                df0.at[df00.columns[n], '標準偏差'] = y.std()
                df0.at[df00.columns[n], '分散'] = variance(y)
                df0.at[df00.columns[n], '最小値'] = y.min()
                df0.at[df00.columns[n], '最大値'] = y.max()
                n += 1

            # 要約統計量（サマリ）のデータフレームを表示
            st.write(df0.style.format("{:.2f}"))

            st.write('【平均値の差の検定（対応なし）】')
            groups = df[cat_var].iloc[:, 0].unique().tolist()

            # 結果を保存するデータフレームの初期化
            columns = ['全体M', '全体S.D', f'{groups[0]}M', f'{groups[0]}S.D',
                       f'{groups[1]}M', f'{groups[1]}S.D', 'df', 't', 'p', 'sign', 'd']
            df_results = pd.DataFrame(columns=columns)

            for var in num_vars:
                series = df[var]
                group0_data = df[df[cat_var[0]] == groups[0]][var]
                group1_data = df[df[cat_var[0]] == groups[1]][var]

                n1 = len(group0_data)
                n2 = len(group1_data)
                s1_sq = np.var(group0_data, ddof=1)
                s2_sq = np.var(group1_data, ddof=1)

                # Welch–Satterthwaiteの式で自由度を計算
                df_numerator = (s1_sq / n1 + s2_sq / n2) ** 2
                df_denominator = ((s1_sq / n1) ** 2) / (n1 - 1) + ((s2_sq / n2) ** 2) / (n2 - 1)
                df_welch = df_numerator / df_denominator

                ttest_result = stats.ttest_ind(group0_data, group1_data, equal_var=False)
                overall_mean = series.mean()
                overall_std = series.std(ddof=1)
                g0_mean = group0_data.mean()
                g0_std = group0_data.std(ddof=1)
                g1_mean = group1_data.mean()
                g1_std = group1_data.std(ddof=1)

                # 効果量dの計算（プールされた標準偏差を使用）
                pooled_std = np.sqrt(((n1 - 1) * s1_sq + (n2 - 1) * s2_sq) / (n1 + n2 - 2))
                effect_size = abs((g0_mean - g1_mean) / pooled_std)

                if ttest_result.pvalue < 0.01:
                    significance = '**'
                elif ttest_result.pvalue < 0.05:
                    significance = '*'
                elif ttest_result.pvalue < 0.1:
                    significance = '†'
                else:
                    significance = 'n.s.'

                results_row = {
                    '全体M': overall_mean,
                    '全体S.D': overall_std,
                    f'{groups[0]}M': g0_mean,
                    f'{groups[0]}S.D': g0_std,
                    f'{groups[1]}M': g1_mean,
                    f'{groups[1]}S.D': g1_std,
                    'df': df_welch,
                    't': abs(ttest_result.statistic),
                    'p': ttest_result.pvalue,
                    'sign': significance,
                    'd': effect_size
                }

                df_results.loc[var] = results_row

            # 結果の表示
            # 数値型の列だけを選択
            numeric_columns = df_results.select_dtypes(include=['float64', 'int64']).columns
            # 選択した列にのみ、スタイルを適用
            styled_df = df_results.style.format({col: "{:.2f}" for col in numeric_columns})
            st.write(styled_df)

            # sign_captionを初期化
            sign_caption = ''

            # 各記号に対するチェックを実行
            if df_results['sign'].str.contains('\*\*').any():
                sign_caption += 'p<0.01** '
            if df_results['sign'].str.contains('\*').any():
                sign_caption += 'p<0.05* '
            if df_results['sign'].str.contains('†').any():
                sign_caption += 'p<0.1† '

            st.caption(sign_caption)

            # サンプルサイズの表示
            st.write('【サンプルサイズ】')
            st.write(f'全体N ＝ {len(df)}')
            st.write(f'● {groups[0]}： {len(df[df[cat_var[0]] == groups[0]])}')
            st.write(f'● {groups[1]}： {len(df[df[cat_var[0]] == groups[1]])}')

            st.subheader('【解釈の補助】')

            for index, row in df_results.iterrows():
                comparison = " < " if row[f'{groups[0]}M'] < row[f'{groups[1]}M'] else " > "
                sign = row['sign']
                if sign in ['**', '*']:
                    significance = "有意な差が生まれる"
                elif sign == '†':
                    significance = "有意な差が生まれる傾向にある"
                else:
                    significance = "有意な差が生まれない"
                p_value = row['p']
                st.write(f'{cat_var_str}によって、{index}には{significance}（{xcat_var_d[0]}{comparison}{xcat_var_d[1]}）（p= {p_value:.2f}）')

            st.subheader('【可視化】')
            # グラフの描画

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
                )

            def create_bracket_shape(x0, x1, y_vline_bottom, bracket_y):
                return dict(
                    type='path',
                    path=f'M {x0},{y_vline_bottom} L{x0},{bracket_y} L{x1},{bracket_y} L{x1},{y_vline_bottom}',
                    line=dict(color='black'),
                    xref='x',
                    yref='y'
                )

            # グラフ描画部分の更新
            for var in num_vars:
                # 各グループのサンプルサイズを取得
                n0 = len(df[df[cat_var[0]] == groups[0]])
                n1 = len(df[df[cat_var[0]] == groups[1]])
                
                # 標準誤差を計算（df_resultsに格納されている標準偏差を利用）
                se0 = df_results.at[var, f'{groups[0]}S.D'] / np.sqrt(n0)
                se1 = df_results.at[var, f'{groups[1]}S.D'] / np.sqrt(n1)
                
                data = pd.DataFrame({
                    '群': groups,
                    '平均値': [df_results.at[var, f'{groups[0]}M'], df_results.at[var, f'{groups[1]}M']],
                    '誤差': [se0, se1] 
                })

                # カテゴリを数値にマッピング
                category_positions = {group: i for i, group in enumerate(data['群'])}
                x_values = [category_positions[group] for group in data['群']]

                fig = go.Figure()

                fig.add_trace(go.Bar(
                    x=x_values,
                    y=data['平均値'],
                    error_y=dict(type='data', array=data['誤差'], visible=True),
                    marker_color='skyblue'
                ))

                # x軸をカテゴリ名で表示
                fig.update_xaxes(
                    tickvals=list(category_positions.values()),
                    ticktext=list(category_positions.keys())
                )

                if show_graph_title:
                    fig.update_layout(title_text=f'平均値の比較： {var} by {cat_var[0]}')

                # 各統計量を取得
                p_value = df_results.at[var, 'p']
                effect_size = df_results.at[var, 'd']
                g0_mean = df_results.at[var, f'{groups[0]}M']
                g0_std = df_results.at[var, f'{groups[0]}S.D']
                g1_mean = df_results.at[var, f'{groups[1]}M']
                g1_std = df_results.at[var, f'{groups[1]}S.D']

                if p_value < 0.01:
                    significance_text = "p < 0.01 **"
                elif p_value < 0.05:
                    significance_text = "p < 0.05 *"
                elif p_value < 0.1:
                    significance_text = "p < 0.1 †"
                else:
                    significance_text = "n.s."

                # 位置の計算
                y0_bar = data['平均値'][0]
                y1_bar = data['平均値'][1]
                e0 = data['誤差'][0]
                e1 = data['誤差'][1]
                y0_top = y0_bar + e0
                y1_top = y1_bar + e1
                y_max_error = max(y0_top, y1_top)
                y_range = y_max_error * 1.1
                y_offset = y_range * 0.05
                bracket_y = y_max_error + y_offset
                vertical_line_offset = y_offset * 0.5
                y_vline_bottom = y_max_error + vertical_line_offset
                annotation_offset = y_offset * 0.5
                annotation_y = bracket_y + annotation_offset

                x0 = x_values[0]
                x1 = x_values[1]

                # ブラケットを追加
                fig.add_shape(create_bracket_shape(x0, x1, y_vline_bottom, bracket_y))
                fig.add_annotation(create_bracket_annotation(x0, x1, annotation_y, significance_text))

                fig.update_yaxes(range=[0, annotation_y + y_offset])

                # 日本語フォントの設定
                fig.update_layout(font=dict(family="IPAexGothic"))

                st.plotly_chart(fig)

                # キャプションの追加
                st.caption(f"【{groups[0]}】 平均値 (SD): {g0_mean:.2f} ( {g0_std:.2f} ), "
                           f"【{groups[1]}】 平均値 (SD): {g1_mean:.2f} ( {g1_std:.2f} ), "
                           f"【危険率】p値: {p_value:.3f},【効果量】d値: {effect_size:.2f}")
                

common.display_copyright()
common.display_special_thanks()
