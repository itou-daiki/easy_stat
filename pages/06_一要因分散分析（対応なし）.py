import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import math
from statistics import median, variance
import matplotlib.pyplot as plt
import japanize_matplotlib
from PIL import Image

st.set_page_config(page_title="一要因分散分析(対応なし)", layout="wide")

st.title("一要因分散分析(対応なし)")
st.caption("Created by Dit-Lab.(Daiki Ito)")
st.write("変数の選択　→　分散分析　→　表作成　→　解釈の補助を行います")
st.write("")

# 分析のイメージ
image = Image.open('anova.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('anova_demo.xlsx', sheet_name=0)
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
        st.write(f'{(cat_var_str)}（{xcat_var_d}）によって、')

        for num_var in num_vars:
            st.write(f'● {num_var}')

        st.write("これらの数値変数に有意な差が生まれるか検定します。")

        # グラフタイトルを表示するチェックボックス
        show_graph_title = st.checkbox('グラフタイトルを表示する', value=True)  # デフォルトでチェックされている

        # t検定の実行
        if st.button('分散分析の実行'):
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
            columns = ['全体M', '全体S.D'] + [item for sublist in zip([f'{group}M' for group in df[cat_var[0]].unique()], [f'{group}S.D' for group in df[cat_var[0]].unique()]) for item in sublist] + \
                    ['df', 'F', 'p', 'sign', 'η²', 'ω²']
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

                sign = '**' if pval < 0.01 else '*' if pval < 0.05 else '†' if pval < 0.1 else 'n.s.'

                df_results.loc[num_var] = [overall_mean, overall_std] + means + stds + [len(df) - len(df[cat_var[0]].unique()), fval, pval, sign, eta_squared, omega_squared]  # 修正: eta_squared, omega_squaredを追加

            # 結果の表示
            # 数値型の列だけを選択
            numeric_columns = df_results.select_dtypes(include=['float64', 'int64']).columns
            # 選択した列にのみ、スタイルを適用
            styled_df = df_results.style.format({col: "{:.2f}" for col in numeric_columns})
            st.write(styled_df)
            
            st.write("【多重比較の結果】")

            for num_var in num_vars:
                # TukeyのHSDテストを実行
                tukey_result = pairwise_tukeyhsd(df[num_var], df[cat_var[0]])
                # 結果をデータフレームに変換
                tukey_df = pd.DataFrame(data=tukey_result._results_table.data[1:], columns=tukey_result._results_table.data[0])
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


            # サンプルサイズの表示
            st.write('＜サンプルサイズ＞')
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

            # ブラケットの位置を格納するリスト
            bracket_spacing = 5
            bracket_length = 1

            def add_bracket(ax, x1, x2, y, p_value, significance, show_bracket=True):
                
                # ブラケットを表示
                if show_bracket:
                    # ブラケットの両端を描画
                    ax.plot([x1, x1], [y, y + bracket_length], color='black', lw=1)
                    ax.plot([x2, x2], [y, y + bracket_length], color='black', lw=1)
        
                    # ブラケットの中央部分を描画
                    ax.plot([x1, x2], [y + bracket_length, y + bracket_length], color='black', lw=1)

                # p値の表示内容を変更
                if significance == '**':
                    p_display = 'p<0.01 **'
                elif significance == '*':
                    p_display = 'p<0.05 *'
                elif significance == '†':
                    p_display = 'p<0.1 †'
                else:
                    p_display = 'n.s.'
                
                # p値と判定記号を表示
                ax.text((x1 + x2) / 2, y + bracket_length + 1, p_display,  # yの位置を調整
                        horizontalalignment='center', verticalalignment='bottom')
                
            for num_var in num_vars:
                # TukeyのHSDテストを実行
                tukey_result = pairwise_tukeyhsd(df[num_var], df[cat_var[0]])
                # 結果をデータフレームに変換
                tukey_df = pd.DataFrame(data=tukey_result._results_table.data[1:], columns=tukey_result._results_table.data[0])

                # 群ごとの平均値と標準偏差を計算
                groups = df.groupby(cat_var[0])
                means = groups[num_var].mean()
                errors = groups[num_var].std()

                # y軸の上限値を計算
                y_max = max(means.values + np.array(errors.values))

                # ブラケットとアノテーションに必要な追加スペースを計算
                additional_space_for_annotation = 5
                
                # すべてのカテゴリ変数のペアを取得
                group_pairs = [(group1, group2) for i, group1 in enumerate(means.index) for j, group2 in enumerate(means.index) if i < j]

                # 有意な差があるペアの数を計算
                num_significant_pairs = sum([p_value < 0.1 for _, _, p_value in tukey_df[['group1', 'group2', 'p-adj']].values])

                # y軸の最大値を計算
                y_axis_max = y_max + (num_significant_pairs * (bracket_spacing + bracket_length)) + additional_space_for_annotation

                # 棒グラフと誤差範囲を描画
                fig, ax = plt.subplots()
                bars = ax.bar(x=means.index, height=means.values, yerr=errors.values, capsize=5)

                # y軸の最大値に基づくブラケットの開始位置を設定
                y_bracket_start = y_max + bracket_spacing

                # ブラケットの位置を格納するリストを初期化
                bracket_positions = []
                
                # ブラケットと判定を追加
                for i, (group1, group2) in enumerate(group_pairs):
                    # tukey_df から特定のペアの p-adj 値を取得
                    matching_row = tukey_df[((tukey_df['group1'] == group1) & (tukey_df['group2'] == group2)) | 
                                            ((tukey_df['group1'] == group2) & (tukey_df['group2'] == group1))]
                    p_value = matching_row['p-adj'].values[0]
                    
                    if p_value < 0.01:
                        significance = '**'
                    elif p_value < 0.05:
                        significance = '*'
                    elif p_value < 0.1:
                        significance = '†'    
                    else:
                        significance = 'n.s.'
                        
                    # group1 と group2 のインデックス位置を取得
                    x1 = means.index.get_loc(group1)
                    x2 = means.index.get_loc(group2)

                    # ブラケットの位置を計算
                    y_position = max(bracket_positions[-1] + bracket_spacing if bracket_positions else y_bracket_start, y_bracket_start)
                    
                    # significance が 'n.s.' でない場合のみ、ブラケットと判定を追加                    
                    if significance != 'n.s.':
                        add_bracket(ax, x1, x2, y_position, p_value, significance)
                        bracket_positions.append(y_position)  # 追加したブラケットの位置を記録

                if show_graph_title:  # チェックボックスの状態に基づいてタイトルを表示または非表示にする
                    ax.set_title(f'{num_var} by {cat_var[0]}')
                ax.set_ylabel(num_var)
                ax.set_xlabel(cat_var[0])
                # y軸の最大値を設定
                ax.set_ylim([0, y_axis_max])
                # グラフを描画
                st.pyplot(fig)



st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.markdown('© 2022-2023 Dit-Lab.(Daiki Ito). All Rights Reserved.')