import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import math
from statistics import median, variance
import matplotlib.pyplot as plt
import japanize_matplotlib
from PIL import Image

st.set_page_config(page_title="一要因分散分析(対応なし)", layout="wide")

st.title("一要因分散分析(対応なし)")
st.caption("Created by Daiki Ito")
st.write("変数の選択　→　分散分析　→　表作成　→　解釈の補助を行います")
st.write("")

# フォント設定
plt.rcParams['font.family'] = 'ipaexg.ttf'

# 分析のイメージ
image = Image.open('ttest.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('ttest_demo.xlsx', sheet_name=0)
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
    cat_var = st.multiselect('カテゴリ変数を選択してください', categorical_cols)

    # 数値変数の選択
    st.subheader("数値変数の選択")
    num_vars = st.multiselect('数値変数を選択してください', numerical_cols)

    # エラー処理
    if not cat_var:
        st.error("カテゴリ変数を選択してください。")
    elif not num_vars:
        st.error("数値変数を選択してください。")
    elif len(df[cat_var].iloc[:, 0].unique()) < 3:
        st.error("独立変数が2群になっていないます、分析を実行できません")
    else:
        st.success("分析可能な変数を選択しました。分析を実行します。")

        # 独立変数から重複のないデータを抽出し、リストに変換
        xcat_var_d = df[cat_var].iloc[:, 0].unique().tolist()
        st.subheader('【分析前の確認】')
        cat_var_str = str(cat_var)
        
        # xcat_var_dの要素をst.writeで表示
        st.write(f'{(cat_var_str)}（{xcat_var_d[0]}）によって、')

        for num_var in num_vars:
            st.write(f'● {num_var}')

        st.write("これらの数値変数に有意な差が生まれるか検定します。")

        # t検定の実行
        if st.button('t検定の実行'):
            st.subheader('【分析結果】')
            st.write('【要約統計量】')

            # 数値変数の要素の数を取得
            num_range = len(num_vars)

            # 各値の初期化
            n = 1
            summaryList = [num_vars]
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

            st.write('【分散分析（対応なし）】')
            
            # ANOVAの実行
            # 結果の表作成
            columns = ['全体M', '全体S.D'] + [f'{group}M' for group in df[cat_var[0]].unique()] + \
                          [f'{group}S.D' for group in df[cat_var[0]].unique()] + ['df', 'F', 'p', 'sign', 'η²', 'ω²']  # 修正: 'η²', 'ω²'を追加
            df_results = pd.DataFrame(columns=columns, index=[num_var])
            
            for num_var in num_vars:
                groups = [df[df[cat_var[0]] == group][num_var] for group in df[cat_var[0]].unique()]
                overall_mean = df[num_var].mean()
                fval, pval = stats.f_oneway(*groups)
                anova_results = stats.f_oneway(*groups)
                df_between = len(df[cat_var[0]].unique()) - 1
                df_within = len(df) - len(df[cat_var[0]].unique())
                ss_between = df_between * sum([(group.mean() - overall_mean)**2 for group in groups])
                ss_total = sum([(value - overall_mean)**2 for group in groups for value in group])
                ms_within = (ss_total - ss_between) / df_within

                # 効果量の計算
                eta_squared = ss_between / ss_total
                omega_squared = (ss_between - (df_between * ms_within)) / (ss_total + ms_within)
                
                overall_std = df[num_var].std()

                means = [group.mean() for group in groups]
                stds = [group.std() for group in groups]

                sign = '**' if pval < 0.01 else '*' if pval < 0.05 else 'n.s.'

                df_results.loc[num_var] = [overall_mean, overall_std] + means + stds + [len(df) - len(df[cat_var[0]].unique()), fval, pval, sign, eta_squared, omega_squared]  # 修正: eta_squared, omega_squaredを追加

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
            st.write('サンプルサイズ')
            st.write(f'全体N ＝ {len(df)}')
            for group_name in df[cat_var[0]].unique():
                st.write(f'● {group_name}： {len(df[df[cat_var[0]] == group_name])}')

            st.subheader('【解釈の補助】')

            for index, row in df_results.iterrows():
                comparisons = "、".join([f'「{xcat_var_d[i]}」 < 「{xcat_var_d[j]}」' for i in range(len(xcat_var_d)) for j in range(i+1, len(xcat_var_d))])
                sign = row['sign']
                if sign in ['**', '*']:
                    significance = "有意な差が生まれる"
                elif sign == '†':
                    significance = "有意な差が生まれる傾向にある"
                else:
                    significance = "有意な差が生まれない"
                p_value = row['p']
                st.write(f'{cat_var_str}によって、【{index}】には{significance}')
                st.write(f'　{comparisons}、（ p = {p_value:.2f} ）')


            st.subheader('【可視化】')
            # グラフの描画
            font_path = 'ipaexg.ttf'
            plt.rcParams['font.family'] = 'IPAexGothic'

            def add_bracket(ax, x1, x2, y, text):
                bracket_length = 4
                ax.annotate("", xy=(x1, y), xycoords='data',
                            xytext=(x1, y + bracket_length), textcoords='data',
                            arrowprops=dict(arrowstyle="-", linewidth=1))
                ax.annotate("", xy=(x2, y), xycoords='data',
                            xytext=(x2, y + bracket_length), textcoords='data',
                            arrowprops=dict(arrowstyle="-", linewidth=1))
                ax.annotate("", xy=(x1 - 0.01, y + bracket_length - 0.5), xycoords='data',
                            xytext=(x2 + 0.01, y + bracket_length - 0.5), textcoords='data',
                            arrowprops=dict(arrowstyle="-", linewidth=1))
                ax.text((x1 + x2) / 2, y + bracket_length + 2, text,
                        horizontalalignment='center', verticalalignment='bottom')

            for var in num_vars:
                data = pd.DataFrame({
                    '群': groups,
                    '平均値': [df_results.at[var, f'{groups[0]}M'], df_results.at[var, f'{groups[1]}M']],
                    '誤差': [df_results.at[var, f'{groups[0]}S.D'], df_results.at[var, f'{groups[1]}S.D']]
                })
                
                

                fig, ax = plt.subplots(figsize=(8, 6))
                bars = ax.bar(x=data['群'], height=data['平均値'], yerr=data['誤差'], capsize=5)
                ax.set_title(f'平均値の比較： {var}')
                p_value = df_results.at[var, 'p']
                if p_value < 0.01:
                    significance_text = "p < 0.01 **"
                elif p_value < 0.05:
                    significance_text = "p < 0.05 **"
                else:
                    significance_text = "n.s."
                ax.set_ylim([0, max(data['平均値']) + max(data['誤差']) + 20])
                add_bracket(ax, 0, 1, max(data['平均値']) + max(data['誤差']) + 5, significance_text)
                st.pyplot(fig)
            
            # 全ての図を一つのフィギュアに結合して描画

            # 結合された図の縦軸を揃える
            
            y_max = max([max(data['平均値']) + max(data['誤差']) *1.5 for var in num_vars])
            fig, axs = plt.subplots(1, len(num_vars), figsize=(8*len(num_vars), 6), sharey=True)  # sharey=Trueで縦軸を揃える
            for i, var in enumerate(num_vars):
                ax = axs[i]  # 各図の座標軸を取得
                data = pd.DataFrame({
                    '群': groups,
                    '平均値': [df_results.at[var, f'{groups[0]}M'], df_results.at[var, f'{groups[1]}M']],
                    '誤差': [df_results.at[var, f'{groups[0]}S.D'], df_results.at[var, f'{groups[1]}S.D']]
                })

                bars = ax.bar(x=data['群'], height=data['平均値'], yerr=data['誤差'], capsize=5, zorder=3)  # zorder parameter added
                ax.yaxis.grid(True, zorder=1)  # y軸のグリッド（横線）を表示, zorder parameter added

                # 軸の横線を繋げる（隣接する軸の横線を繋げる）
                if i > 0:
                    prev_ax = axs[i - 1]
                    ylim = prev_ax.get_ylim()
                    ax.set_ylim(ylim)

                ax.set_title(f'平均値の比較： {var}')
                p_value = df_results.at[var, 'p']
                if p_value < 0.01:
                    significance_text = "p < 0.01 **"
                elif p_value < 0.05:
                    significance_text = "p < 0.05 **"
                else:
                    significance_text = "n.s."

                add_bracket(ax, 0, 1, max(data['平均値']) + max(data['誤差']) + 5, significance_text)
                ax.set_ylim([0, y_max*1.5])  # 各図の縦軸の最大値を揃える
                ax.spines['top'].set_visible(False)  # 上の枠線を消す
                ax.spines['right'].set_visible(False)  # 右の枠線を消す
                ax.spines['left'].set_visible(False)  # 左の枠線を消す
                ax.spines['bottom'].set_visible(False)  # 下の枠線を消す

                ax.yaxis.grid(True)  # y軸のグリッド（横線）を表示

            st.pyplot(fig)  # 結合されたフィギュアを表示


st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
