import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statistics import median, variance
import matplotlib.pyplot as plt
import japanize_matplotlib
from PIL import Image

# Streamlitのページ設定
st.set_page_config(page_title="二要因分散分析(対応なし)", layout="wide")

# タイトルと説明
st.title("二要因分散分析(対応なし)")
st.caption("Created by Dit-Lab.(Daiki Ito)")
st.write("変数の選択 → 分散分析 → 表作成 → 解釈の補助を行います")
st.write("")

# 分析のイメージ
image = Image.open('anova.png')  # 画像のパスは適宜変更してください
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('anova_demo.xlsx', sheet_name=0)  # デモデータのパスは適宜変更してください
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
    cat_vars = st.multiselect('2つのカテゴリ変数を選択してください', categorical_cols, format_func=lambda x: x, default=categorical_cols[:2])

    # 数値変数の選択
    st.subheader("数値変数の選択")
    num_var = st.selectbox('数値変数を選択してください', numerical_cols)

    # エラー処理
    if len(cat_vars) != 2:
        st.error("2つのカテゴリ変数を選択してください。")
    elif not num_var:
        st.error("数値変数を選択してください。")
    else:
        st.success("分析可能な変数を選択しました。分析を実行します。")

        # two-way ANOVAの実行
        if st.button('分散分析の実行'):
            st.subheader('【分析結果】')

            # formulaの生成
            # カテゴリ変数が日本語や特殊文字を含む場合、バッククォートで囲む
            formula = f'Q("{num_var}") ~ C(Q("{cat_vars[0]}")) + C(Q("{cat_vars[1]}")) + C(Q("{cat_vars[0]}")):C(Q("{cat_vars[1]}"))'
            try:
                model = ols(formula, df).fit()
                anova_results = anova_lm(model, typ=2)
                st.write(anova_results)
            except Exception as e:
                st.error(f"分析中にエラーが発生しました: {e}")

            # TukeyのHSDテストと可視化
            st.write("【多重比較の結果】")
            tukey_results = {}
            for cat in cat_vars:
                tukey = pairwise_tukeyhsd(endog=df[num_var], groups=df[cat], alpha=0.05)
                tukey_results[cat] = tukey

                # Tukey結果をDataFrameに変換して列名を適切なものに変更
                tukey_df = pd.DataFrame(data=tukey._results_table.data[1:], columns=tukey._results_table.data[0])
                tukey_df.columns = ['Group1', 'Group2', 'Meandiff', 'P-adj', 'Lower', 'Upper', 'Reject']
                tukey_df = tukey_df.rename(columns={'Group1': f'{cat}1', 'Group2': f'{cat}2'})

                st.write(f'＜ {cat} に対する多重比較の結果 ＞')
                st.table(tukey_df)

            # 可視化
            st.subheader('【可視化】')
            plt.rcParams['font.family'] = 'IPAexGothic'
            fig, ax = plt.subplots(figsize=(10, 6))

            # カテゴリ変数ごとにデータを集計
            means = df.groupby(cat_vars)[num_var].mean().unstack()
            errors = df.groupby(cat_vars)[num_var].std().unstack()

            # データのプロット
            means.plot(kind='bar', yerr=errors, ax=ax, capsize=5)

            # ブラケットとアノテーションを追加する関数
            def add_significance_brackets(cat, group1, group2, height, display_text):
                x1, x2 = means.index.get_loc(group1), means.index.get_loc(group2)
                ax.plot([x1, x1, x2, x2], [height, height + 0.02, height + 0.02, height], lw=1.5, c='black')
                ax.text((x1 + x2) * 0.5, height + 0.02, display_text, ha='center', va='bottom')

            # すべての組み合わせについてブラケットを追加
            height = means.values.max() + errors.values.max() + 0.05
            for cat in cat_vars:
                unique_groups = df[cat].unique()
                for i, group1 in enumerate(unique_groups):
                    for j, group2 in enumerate(unique_groups):
                        if i < j:
                            # 正しいインデックスでp値を取得
                            p_value = tukey_results[cat].pvalues[unique_groups.tolist().index(group1) * len(unique_groups) + unique_groups.tolist().index(group2)]
                            if p_value < 0.05:
                                display_text = f'p = {p_value:.3f}'
                                add_significance_brackets(cat, group1, group2, height, display_text)
                                height += 0.05

            plt.title(f'{num_var} by {cat_vars[0]} and {cat_vars[1]}')
            plt.ylabel(num_var)
            plt.xlabel('Categories')
            st.pyplot(fig)

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
# Copyright
st.subheader('© 2022-2024 Dit-Lab.(Daiki Ito). All Rights Reserved.')
st.write("easyStat: Open Source for Ubiquitous Statistics")
st.write("Democratizing data, everywhere.")
st.write("")
st.subheader("In collaboration with our esteemed contributors:")
st.write("・Toshiyuki")
st.write("With heartfelt appreciation for their dedication and support.")
