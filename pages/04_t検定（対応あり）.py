import streamlit as st
import math
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import japanize_matplotlib
from scipy import stats
from PIL import Image
from statistics import median, variance

import matplotlib as mpl
# フォントのプロパティを設定
font_prop = mpl.font_manager.FontProperties(fname="ipaexg.ttf")
# Matplotlibのデフォルトのフォントを変更
mpl.rcParams['font.family'] = font_prop.get_name()

st.set_page_config(page_title="t検定(対応あり)", layout="wide")

st.title("t検定(対応あり)")
st.caption("Created by Daiki Ito")
st.write("")
st.subheader("ブラウザでt検定　→　表　→　解釈まで出力できるウェブアプリです。")
st.write("iPad等でも分析を行うことができます")
st.write("")

st.subheader("【注意事項】")
st.write("Excelファイルに不備があるとエラーが出ます")
st.write('<span style="color:blue">デフォルトでデモ用データの分析ができます。</span>',
         unsafe_allow_html=True)
st.write(
    '<span style="color:blue">ファイルをアップせずに「データフレームの表示」ボタンを押すと　'
    'デモ用のデータを確認できます。</span>',
    unsafe_allow_html=True)
st.write('<span style="color:red">欠損値を含むレコード（行）は自動で削除されます。</span>',
         unsafe_allow_html=True)

code = '''
#使用ライブラリ
import streamlit as st
import pandas as pd
from scipy import stats
from PIL import Image
from statistics import median, variance
'''

st.code(code, language='python')

# Excelデータの例
image = Image.open('ttest_rel.png')
st.image(image)

# 変数設定の注意点
if st.checkbox('注意点の表示（クリックで開きます）'):
    attentionImage = Image.open('ttest_rel_attention.png')
    st.image(attentionImage)

# デモ用ファイル
df = pd.read_excel('ttest_rel_demo.xlsx', sheet_name=0)

# xlsx, csvファイルのアップロード
upload_files = st.file_uploader("ファイルアップロード", type=['xlsx', 'csv'])

# xlsx, csvファイルの読み込み → データフレームにセット
if upload_files:
    # dfを初期化
    df.drop(range(len(df)))
    # ファイルの拡張子によって読み込み方法を変える
    if upload_files.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        # xlsxファイルの読み込み → データフレームにセット
        df = pd.read_excel(upload_files, sheet_name=0)
    elif upload_files.type == 'text/csv':
        # csvファイルの読み込み → データフレームにセット
        df = pd.read_csv(upload_files)
    # 欠損値を含むレコードを削除
    df.dropna(how='any', inplace=True)

# データフレーム表示ボタン
if st.checkbox('データフレームの表示（クリックで開きます）'):
    st.dataframe(df, width=0)

# 変数選択フォーム
with st.form(key='variable_form'):
    st.subheader("分析に使用する変数（観測値、測定値）の選択")

    # 観測値と測定値のセット
    ovList = df.columns.tolist()
    mvList = df.columns.tolist()

    # 複数選択（観測値）
    ObservedVariable = st.multiselect('観測値（複数選択可）', ovList)

    # 複数選択（測定値）
    MeasuredVariable = st.multiselect('測定値（複数選択可）', mvList)

    st.write(
        '<span style="color:blue">【注意】従属変数に数値以外のものがある場合、分析できません</span>',
        unsafe_allow_html=True)

    # 変数の個数があってないときの処理
    ovRange = len(ObservedVariable)
    mvRange = len(MeasuredVariable)

    if ovRange != mvRange:
        st.write(
            '<span style="color:red">観測値の数と測定値の数を合わせてください</span>',
            unsafe_allow_html=True)
    else:
        st.write(
            '<span style="color:green">分析可能です</span>',
            unsafe_allow_html=True)

    # 確認ボタンの表示
    CHECK_btn = st.form_submit_button('確認')

# 分析前の確認フォーム
with st.form(key='check_form'):
    if CHECK_btn:
        st.subheader('【分析前の確認】')

        n = 0
        for ViewCheck in range(ovRange):
            st.write(
                f'● 【'f'{(ObservedVariable[n])}'f'】　→　【'f'{(MeasuredVariable[n])}】')
            n += 1
        st.write('    '+'これらの観測値と実測値の間に有意な差が生まれるか検定します。')

    # 分析実行ボタンの表示
    TTEST_btn = st.form_submit_button('分析実行')

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
        summaryColumns = ["観測値" + "M", "観測値" + "S.D",
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
                '群': [ObservedVariable, MeasuredVariable],
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
