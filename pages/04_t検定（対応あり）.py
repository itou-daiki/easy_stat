import streamlit as st
import pandas as pd
from scipy import stats
import math
from statistics import median, variance
import matplotlib.pyplot as plt
import japanize_matplotlib
from PIL import Image

st.set_page_config(page_title="t検定(対応あり)", layout="wide")

st.title("t検定(対応あり)")
st.caption("Created by Daiki Ito")
st.write("変数の選択　→　t検定　→　表作成　→　解釈の補助を行います")
st.write("")

# フォント設定
plt.rcParams['font.family'] = 'ipaexg.ttf'

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
    pre_vars = st.multiselect('観測変数を選択してください', numerical_cols)

    numerical_cols.remove(pre_vars)  # 選択済みの変数をリストから削除
    
    st.subheader("測定変数の選択")
    post_vars = st.multiselect('測定変数を選択してください', numerical_cols)
    
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
            st.subheader('&#8203;``【oaicite:0】``&#8203;')
            
            # 検定結果のデータフレームを作成
            resultColumns = ["観測値" + "M", "観測値" + "S.D",
                            "測定値" + "M", "測定値" + "S.D",
                            'df', 't', 'p', 'sign', 'd']

            # indexにpre → post となるようにデータフレームを記載
            index = [f'{pre_var} → {post_var}' for pre_var, post_var in zip(pre_vars, post_vars)]
            result_df = pd.DataFrame(index=index, columns=resultColumns)

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
            st.write(result_df)

            for pre_var, post_var in zip(pre_vars, post_vars):
                st.write(f'{pre_var} → {post_var}')
                
                # t検定
                ttest_result = stats.ttest_rel(df[pre_var], df[post_var])
                
                # 結果の表示
                st.write(f't値: {ttest_result.statistic:.2f}')
                st.write(f'p値: {ttest_result.pvalue:.2f}')

                # グラフの描画
                fig, ax = plt.subplots()
                ax.boxplot([df[pre_var], df[post_var]])
                ax.set_xticklabels([pre_var, post_var])
                st.pyplot(fig)


st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9',
         'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
