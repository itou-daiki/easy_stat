import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import math
from statistics import median, variance
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import japanize_matplotlib
from PIL import Image

st.set_page_config(page_title="t検定(対応あり)", layout="wide")

st.title("t検定(対応あり)")
st.caption("Created by Daiki Ito")
st.write("変数の選択　→　t検定　→　表作成　→　解釈の補助を行います")
st.write("")

# 分析のイメージ
image = Image.open('ttest_rel.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('ttest_rel_demo.xlsx', sheet_name=0)
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

        # t検定の実行
        if st.button('t検定の実行'):
            st.subheader('【分析結果】')
            st.write("【要約統計量】")
            
            # 数値変数のリスト
            num_vars = numerical_cols

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
                df_summary.at[var, '標準偏差'] = y.std()
                df_summary.at[var, '分散'] = variance(y)
                df_summary.at[var, '最小値'] = y.min()
                df_summary.at[var, '最大値'] = y.max()

            # 要約統計量（サマリ）のデータフレームを表示
            st.write(df_summary.style.format("{:.2f}"))

            st.write("【平均値の差の検定（対応あり）】")
            
            # 検定結果のデータフレームを作成
            resultColumns = ["観測値" + "M", "観測値" + "S.D",
                            "測定値" + "M", "測定値" + "S.D",
                            'df', 't', 'p', 'sign', 'd']

            # indexにpre → post となるようにデータフレームを記載
            index = [f'{pre_var} → {post_var}' for pre_var, post_var in zip(pre_vars, post_vars)]
            result_df = pd.DataFrame(index=index, columns=resultColumns)
            paired_variable_list = [f'{pre_var} → {post_var}' for pre_var, post_var in zip(pre_vars, post_vars)]

            for pre_var, post_var, idx in zip(pre_vars, post_vars, index):
                # t値、p値、s（全体標準偏差）、d値（効果量）の取得
                x, y = df[pre_var], df[post_var]
                ttest = stats.ttest_rel(x, y)
                t = abs(ttest.statistic)
                p = ttest.pvalue
                xs, ys = x.std(), y.std()
                xm, ym = x.mean(), y.mean()
                d_beta = xm - ym
                xdf, ydf = len(x), len(y)
                px, py = pow(xs, 2), pow(ys, 2)
                ds = math.sqrt(((xdf * px) + (ydf * py)) / (xdf + ydf))
                d = abs(d_beta / ds)

                # p値の判定をsignに格納
                sign = ""
                if p < 0.01:
                    sign = "**"
                elif p < 0.05:
                    sign = "*"
                elif p < 0.1:
                    sign = "†"
                else:
                    sign = "n.s."

                # 従属変数の列データの計算処理
                result_df.at[idx, '観測値M'] = xm
                result_df.at[idx, '観測値S.D'] = xs
                result_df.at[idx, '測定値M'] = ym
                result_df.at[idx, '測定値S.D'] = ys
                result_df.at[idx, 'df'] = len(x) - 1
                result_df.at[idx, 't'] = t
                result_df.at[idx, 'p'] = p
                result_df.at[idx, 'sign'] = sign
                result_df.at[idx, 'd'] = d

            # 結果のデータフレームを表示
            # r_numerical_cols = result_df.select_dtypes(exclude=['object', 'category']).columns.tolist()
            # result_df[r_numerical_cols] = result_df[r_numerical_cols].apply(pd.to_numeric, errors='coerce')
            # styled_df = result_df.style.format({col: "{:.2f}" for col in r_numerical_cols})
            st.write(result_df) 

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
            # 'sign'列、'観測値M'列、および'測定値M'列の列番号を取得
            sign_col = result_df.columns.get_loc('sign')
            x_mean_col = result_df.columns.get_loc("観測値M")
            y_mean_col = result_df.columns.get_loc("測定値M")

            # paired_variable_listを直接イテレートして、各変数に対して解釈を提供
            for idx, vn in enumerate(paired_variable_list):
                # p値の解釈を取得
                interpretation = ""
                comparison = "＞" if result_df.iat[idx, x_mean_col] > result_df.iat[idx, y_mean_col] else "＜"

                if result_df.iat[idx, sign_col] == "**" or result_df.iat[idx, sign_col] == "*":
                    interpretation = f'{vn}には有位な差が生まれる（ 観測値　{comparison}　測定値 ）'
                elif result_df.iat[idx, sign_col] == "†":
                    interpretation = f'{vn}には有意な差が生まれる傾向にある（ 観測値　{comparison}　測定値 ）'
                elif result_df.iat[idx, sign_col] == "n.s.":
                    interpretation = f'{vn}には有意な差が生まれない'
                # 解釈を表示
                st.write(f'●{interpretation}（p={result_df.iat[idx, result_df.columns.get_loc("p")]:.2f}）')

            st.subheader('【可視化】')

            # グラフの描画
            font_path = 'ipaexg.ttf'
            plt.rcParams['font.family'] = 'IPAexGothic'

            # ブラケット付きの棒グラフを出力する機能の追加
            def add_bracket(ax, x1, x2, y, text):
                bracket_length = 4
                # ブラケットの両端を描画
                ax.add_line(Line2D([x1, x1], [y, y + bracket_length], color='black', lw=1))
                ax.add_line(Line2D([x2, x2], [y, y + bracket_length], color='black', lw=1))

                # ブラケットの中央部分を描画
                ax.add_line(Line2D([x1, x2], [y + bracket_length, y + bracket_length], color='black', lw=1))

                # p値と判定記号を表示
                ax.text((x1 + x2) / 2, y + bracket_length + 2, text,
                        horizontalalignment='center', verticalalignment='bottom')

            for pre_var, post_var in zip(pre_vars, post_vars):
                data = pd.DataFrame({
                    '群': [pre_var, post_var],
                    '平均値': [df[pre_var].mean(), df[post_var].mean()],
                    '誤差': [df[pre_var].std(), df[post_var].std()]
                })

                fig, ax = plt.subplots(figsize=(8, 6))
                bars = ax.bar(x=data['群'], height=data['平均値'], yerr=data['誤差'], capsize=5)
                ax.set_title(f'平均値の比較： {pre_var} → {post_var}')
                ttest_result = stats.ttest_rel(df[pre_var], df[post_var])
                p_value = ttest_result.pvalue
                if p_value < 0.01:
                    significance_text = "p < 0.01 **"
                elif p_value < 0.05:
                    significance_text = "p < 0.05 *"
                elif p_value < 0.1:
                    significance_text = "p < 0.10 †"
                else:
                    significance_text = "n.s."
                ax.set_ylim([0, (max(data['平均値']) + max(data['誤差']))*1.4])  
                add_bracket(ax, 0, 1, max(data['平均値']) + max(data['誤差']) + 5, significance_text)
                st.pyplot(fig)

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9','まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
