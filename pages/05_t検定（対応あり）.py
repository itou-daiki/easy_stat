from statistics import median, variance

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from scipy import stats

import common


st.set_page_config(page_title="t検定(対応あり)", layout="wide")

st.title("t検定(対応あり)")
common.display_header()
st.write("変数の選択　→　t検定　→　表作成　→　解釈の補助を行います")
st.write("")

# 分析のイメージ
image = Image.open('images/ttest_rel.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('datasets/ttest_rel_demo.xlsx', sheet_name=0)
    st.write(df.head())
else:
    if uploaded_file is not None:
        if uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
            st.write(df.head())
        else:
            df = pd.read_excel(uploaded_file)
            st.write(df.head())

# 変数設定の注意点
if st.checkbox('注意点の表示（クリックで開きます）'):
    attentionImage = Image.open('ttest_rel_attention.png')
    st.image(attentionImage)

if df is not None:
    # 数値変数の抽出
    numerical_cols = df.select_dtypes(exclude=['object', 'category']).columns.tolist()

    # 観測変数と測定変数の選択
    st.subheader("観測変数の選択")
    pre_vars = st.multiselect('観測変数を選択してください', numerical_cols, key='pre_vars')

    # 選択済みの変数をリストから削除
    remaining_cols = [col for col in numerical_cols if col not in pre_vars]
    
    st.subheader("測定変数の選択")
    post_vars = st.multiselect('測定変数を選択してください', remaining_cols, key='post_vars')
    
    # エラー処理
    if len(pre_vars) != len(post_vars):
        st.error("観測変数と測定変数の数は同じでなければなりません。")
    elif not pre_vars or not post_vars:
        st.error("観測変数と測定変数を選択してください。")
    else:
        st.success("分析可能な変数を選択しました。分析を実行します。")

        st.subheader("分析前の確認")

        # pre_varsとpost_varsのリストを順番にイテレートし、それぞれの変数のペアを表示
        for pre_var, post_var in zip(pre_vars, post_vars):
            st.write(f'● {pre_var} → {post_var}')
        
        st.write("これらの数値変数に有意な差が生まれるか検定します。")

        # グラフタイトルを表示するチェックボックス
        show_graph_title = st.checkbox('グラフタイトルを表示する', value=True)  # デフォルトでチェックされている

        # t検定の実行
        if st.button('t検定の実行'):
            st.subheader('【分析結果】')
            st.write("【要約統計量】")
            
            # 数値変数のリスト
            num_vars = pre_vars + post_vars

            # サマリ用のデータフレームのセット
            summaryColumns = ["有効N", "平均値", "中央値", "標準偏差", "分散",
                              "最小値", "最大値"]
            df_summary = pd.DataFrame(index=num_vars, columns=summaryColumns)

            # サマリ用のデータフレームに平均値と標準偏差を追加
            for var in num_vars:
                y = df[var]
                df_summary.at[var, '有効N'] = len(y)
                df_summary.at[var, '平均値'] = y.mean()
                df_summary.at[var, '中央値'] = median(y)
                df_summary.at[var, '標準偏差'] = y.std(ddof=1)
                df_summary.at[var, '分散'] = variance(y)
                df_summary.at[var, '最小値'] = y.min()
                df_summary.at[var, '最大値'] = y.max()

            # 要約統計量（サマリ）のデータフレームを表示
            st.write(df_summary.style.format("{:.2f}"))

            st.write("【平均値の差の検定（対応あり）】")
            
            # 検定結果のデータフレームを作成
            resultColumns = ["観測値M", "観測値S.D",
                            "測定値M", "測定値S.D",
                            'df', 't', 'p', 'sign', 'd']
            index = [f'{pre_var} → {post_var}' for pre_var, post_var in zip(pre_vars, post_vars)]
            result_df = pd.DataFrame(index=index, columns=resultColumns)
            paired_variable_list = [f'{pre_var} → {post_var}' for pre_var, post_var in zip(pre_vars, post_vars)]

            for pre_var, post_var, idx in zip(pre_vars, post_vars, index):
                x = df[pre_var]
                y = df[post_var]
                n = len(x)

                # 対応のあるt検定
                ttest = stats.ttest_rel(x, y)
                t = ttest.statistic
                p = ttest.pvalue
                df_t = n - 1  # 自由度

                # 平均値と標準偏差
                x_mean = x.mean()
                y_mean = y.mean()
                x_std = x.std(ddof=1)
                y_std = y.std(ddof=1)

                # 効果量dの計算（対応のあるデータの標準偏差を使用）
                diff = x - y
                d = abs((x_mean - y_mean) / diff.std(ddof=1))

                # p値の判定をsignに格納
                if p < 0.01:
                    sign = "**"
                elif p < 0.05:
                    sign = "*"
                elif p < 0.1:
                    sign = "†"
                else:
                    sign = "n.s."

                # 結果をデータフレームに格納
                result_df.at[idx, '観測値M'] = x_mean
                result_df.at[idx, '観測値S.D'] = x_std
                result_df.at[idx, '測定値M'] = y_mean
                result_df.at[idx, '測定値S.D'] = y_std
                result_df.at[idx, 'df'] = df_t
                result_df.at[idx, 't'] = t
                result_df.at[idx, 'p'] = p
                result_df.at[idx, 'sign'] = sign
                result_df.at[idx, 'd'] = d

            # 結果のデータフレームを表示
            numeric_columns = result_df.select_dtypes(include=['float64', 'int64']).columns
            styled_df = result_df.style.format({col: "{:.2f}" for col in numeric_columns})
            st.write(styled_df)

            # sign_captionを初期化
            sign_caption = ''

            # 各記号に対するチェックを実行
            if result_df['sign'].str.contains('\*\*').any():
                sign_caption += 'p<0.01** '
            if result_df['sign'].str.contains('\*').any():
                sign_caption += 'p<0.05* '
            if result_df['sign'].str.contains('†').any():
                sign_caption += 'p<0.1† '

            st.caption(sign_caption)

            # サンプルサイズの表示
            st.write('【サンプルサイズ】')
            st.write(f'全体N ＝ {len(df)}')

            st.subheader('【解釈の補助】')
            # paired_variable_listを直接イテレートして、各変数に対して解釈を提供
            for idx, vn in enumerate(paired_variable_list):
                # p値の解釈を取得
                sign = result_df.iloc[idx]['sign']
                x_mean = result_df.iloc[idx]['観測値M']
                y_mean = result_df.iloc[idx]['測定値M']
                p_value = result_df.iloc[idx]['p']

                comparison = "＞" if x_mean > y_mean else "＜"

                if sign in ["**", "*"]:
                    interpretation = f'{vn}には有意な差が生まれる（観測値 {comparison} 測定値）'
                elif sign == "†":
                    interpretation = f'{vn}には有意な差が生まれる傾向にある（観測値 {comparison} 測定値）'
                else:
                    interpretation = f'{vn}には有意な差が生まれない'

                # 解釈を表示
                st.write(f'● {interpretation}（p= {p_value:.2f}）')

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
                )

            def create_bracket_shape(x0, x1, y_vline_bottom, bracket_y):
                return dict(
                    type='path',
                    path=f'M {x0},{y_vline_bottom} L{x0},{bracket_y} L{x1},{bracket_y} L{x1},{y_vline_bottom}',
                    line=dict(color='black'),
                    xref='x',
                    yref='y'
                )

            # グラフ描画部分
            for pre_var, post_var in zip(pre_vars, post_vars):
                x = df[pre_var]
                y = df[post_var]
                n = len(x)
                data = pd.DataFrame({
                    '群': [pre_var, post_var],
                    '平均値': [x.mean(), y.mean()],
                    '誤差': [x.std(ddof=1) / np.sqrt(n), y.std(ddof=1) / np.sqrt(n)]  # 標準誤差に修正
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
                    fig.update_layout(title_text=f'平均値の比較： {pre_var} → {post_var}')

                # 各統計量を取得
                ttest_result = stats.ttest_rel(x, y)
                t = ttest_result.statistic
                p_value = ttest_result.pvalue
                n = len(x)
                df_t = n - 1  # 自由度

                diff = x - y
                d = abs((x.mean() - y.mean()) / diff.std(ddof=1))

                if p_value < 0.01:
                    significance_text = "p < 0.01 **"
                elif p_value < 0.05:
                    significance_text = "p < 0.05 *"
                elif p_value < 0.1:
                    significance_text = "p < 0.1 †"
                else:
                    significance_text = "n.s."

                # 位置を計算
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

                # Excelダウンロードリンク
                excel_data = common.export_plotly_to_excel(fig, filename=f"t検定対応あり_{pre_var}_{post_var}.xlsx", sheet_name="グラフ")
                import base64
                b64 = base64.b64encode(excel_data).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="t検定対応あり_{pre_var}_{post_var}.xlsx" style="text-decoration: none; color: #1f77b4;">📊 グラフをExcelでダウンロード</a>'
                st.markdown(href, unsafe_allow_html=True)

                # キャプションの追加
                st.caption(f"【観測値】 平均値 (SD): {x.mean():.2f} ({x.std(ddof=1):.2f}), "
                           f"【測定値】 平均値 (SD): {y.mean():.2f} ({y.std(ddof=1):.2f}), "
                           f"【危険率】　p値: {p_value:.3f},【効果量】 d値: {d:.2f}")

# フッター
common.display_copyright()
common.display_special_thanks()
