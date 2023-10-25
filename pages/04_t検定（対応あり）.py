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
    
    st.subheader("測定変数の選択")
    post_vars = st.multiselect('測定変数を選択してください', numerical_cols)
    
    # エラー処理
    if len(pre_vars) != len(post_vars):
        st.error("観測変数と測定変数の数は同じでなければなりません。")
    elif not pre_vars or not post_vars:
        st.error("観測変数と測定変数を選択してください。")
    else:
        st.success("分析可能な変数を選択しました。分析を実行します。")

        # t検定の実行
        if st.button('t検定の実行'):
            st.subheader('&#8203;``【oaicite:0】``&#8203;')
            
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

# 分析結果表示フォーム
with st.form(key='analyze_form'):
    if TTEST_btn:
        st.subheader('【分析結果】')

        # 各値の初期化
        n = 1
        m = 0
        # リストの名前を取得
        VariableList = []
        for ListAppend in range(ovRange):
            VariableList.append(
                f'【'f'{(ObservedVariable[m])}'f'】　→　【'f'{(MeasuredVariable[m])}】')
            m += 1

        # 観測値、測定値から作業用データフレームのセット
        # df00_list = [ovList]
        # df00_list = df00_list + mvList
        dfOv = df[ObservedVariable]
        dfMv = df[MeasuredVariable]

        st.write('【平均値の差の検定（対応あり）】')

        # 各値の初期化
        n = 0
        # t検定結果用データフレーム（df1）の列を指定
        resultColumns = ["観測値" + "M", "観測値" + "S.D",
                          "測定値" + "M", "測定値" + "S.D",
                          'df', 't', 'p', 'sign', 'd']

        df1 = pd.DataFrame(index=VariableList, columns=summaryColumns)

        for ttest_rel in range(ovRange):
            # 列データの取得（nは変数の配列番号）
            x = dfOv.iloc[:, n]
            y = dfMv.iloc[:, n]

            # t値、p値、s（全体標準偏差）、d値（効果量）の取得
            ttest = stats.ttest_rel(x, y)
            t = abs(ttest[0])
            p = ttest[1]
            xs = x.std()
            ys = y.std()
            xm = x.mean()
            ym = y.mean()
            d_beta = xm - ym
            xdf = len(x)
            ydf = len(y)
            px = pow(xs, 2)
            py = pow(ys, 2)
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
            df1.at[VariableList[n], '観測値M'] = xm
            df1.at[VariableList[n], '観測値S.D'] = xs
            df1.at[VariableList[n], '測定値M'] = ym
            df1.at[VariableList[n], '測定値S.D'] = ys
            df1.at[VariableList[n], 'df'] = len(x) - 1
            df1.at[VariableList[n], 't'] = t
            df1.at[VariableList[n], 'p'] = p
            df1.at[VariableList[n], 'sign'] = sign
            df1.at[VariableList[n], 'd'] = d

            n += 1

        st.dataframe(df1)

        # サンプルサイズの取得
        sample_n = len(dfOv)

        st.write('【サンプルサイズ】')
        st.write(f'全体N ＝'f'{sample_n}')

        st.write('【分析結果の解釈】')
        # 各値の初期化、簡素化
        n = 0
        vn = VariableList[n]

        # sign の列番号を取得
        sign_n = df1.columns.get_loc('sign')
        # DivideVariable[0] + 'M' の列番号を取得
        xn = df1.columns.get_loc("観測値M")
        # DivideVariable[1] + 'M' の列番号を取得
        yn = df1.columns.get_loc("測定値M")

        for interpretation in range(ovRange):
            vn = VariableList[n]
            if df1.iat[n, sign_n] == "**":
                if df1.iat[n, xn] > df1.iat[n, yn]:
                    st.write(f'{vn}には有位な差が生まれる（ 観測値　＞　測定値 ）')
                elif df1.iat[n, xn] < df1.iat[n, yn]:
                    st.write(f'{vn}には有位な差が生まれる（ 観測値　＜　測定値 ）')
            elif df1.iat[n, sign_n] == "*":
                if df1.iat[n, xn] > df1.iat[n, yn]:
                    st.write(f'{vn}には有位な差が生まれる（ 観測値　＞　測定値 ）')
                elif df1.iat[n, xn] < df1.iat[n, yn]:
                    st.write(f'{vn}には有位な差が生まれる（ 観測値　＜　測定値 ）')
            elif df1.iat[n, sign_n] == "†":
                if df1.iat[n, xn] > df1.iat[n, yn]:
                    st.write(f'{vn}には有意な差が生まれる傾向にある（ 観測値　＞　測定値 ）')
                elif df1.iat[n, xn] < df1.iat[n, yn]:
                    st.write(f'{vn}には有意な差が生まれる傾向にある（ 観測値　＜　測定値 ）')
            elif df1.iat[n, sign_n] == "n.s.":
                st.write(f'{vn}には有意な差が生まれない')

            data = pd.DataFrame({
            '群': [ObservedVariable[n], MeasuredVariable[n]],
            '平均値': [df1.iat[n, df1.columns.get_loc("観測値M")], df1.iat[n, df1.columns.get_loc("測定値M")]],
            '誤差': [df1.iat[n, df1.columns.get_loc("観測値S.D")], df1.iat[n, df1.columns.get_loc("測定値S.D")]]
            })

            fig, ax = plt.subplots(figsize=(8, 6))

            # Seaborn barplot
            sns.barplot(x='群', y='平均値', data=data, ax=ax, capsize=0.1, errcolor='black', errwidth=1)

            # Add error bars
            ax.errorbar(x=data['群'], y=data['平均値'], yerr=data['誤差'], fmt='none', c='black', capsize=3)

            st.pyplot(fig)

            n += 1

    TTEST_btn = st.form_submit_button('OK')

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9',
         'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
