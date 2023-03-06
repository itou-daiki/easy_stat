import streamlit as st
import pandas as pd
# 実装予定
# import matplotlib.pyplot as plt
# import japanize_matplotlib
from scipy import stats
from PIL import Image
from statistics import median, variance

st.set_page_config(page_title="ブラウザt検定(対応なし)", layout="wide")

st.title("ブラウザt検定(対応なし)")
st.caption("Created by Daiki Ito")
st.write("")
st.subheader("ブラウザでt検定　→　表　→　解釈まで出力できるウェブアプリです。")
st.write("iPad等でも分析を行うことができます")
st.write('対応ありはコチラ→',
         'https://dddd-onigiri-browser-ttest-rel-main-n1g75x.streamlit.app/')
st.write("")

st.subheader("【注意事項】")
st.write('<span style="color:red">群分け変数に数値(0、1等)は使わないでください。</span>',
         unsafe_allow_html=True)
st.write("また、Excelファイルに不備があるとエラーが出ます")
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
image = Image.open('ttest.png')
st.image(image)

# 変数設定の注意点
if st.checkbox('注意点の表示（クリックで開きます）'):
    attentionImage = Image.open('ttest_attention.png')
    st.image(attentionImage)

# デモ用ファイル
df = pd.read_excel('ttest_demo.xlsx', sheet_name=0)

# xlsxファイルのアップロード
upload_files_xlsx = st.file_uploader("ファイルアップロード", type='xlsx')

# xlsxファイルの読み込み → データフレームにセット
if upload_files_xlsx:
    # dfを初期化
    df.drop(range(len(df)))
    # xlsxファイルの読み込み → データフレームにセット
    df = pd.read_excel(upload_files_xlsx, sheet_name=0)
    # 欠損値を含むレコードを削除
    df.dropna(how='any', inplace=True)

# データフレーム表示ボタン
if st.checkbox('データフレームの表示（クリックで開きます）'):
    st.dataframe(df, width=0)

# 変数選択フォーム
with st.form(key='variable_form'):
    st.subheader("分析に使用する変数の選択")
    st.write("")
    st.write(
        "ファイルをアップロードした場合、確認ボタンを２回押さないと独立変数の判定が出ません（アップデート予定）")

    # 独立変数と従属変数のセット
    ivList = df.columns.tolist()
    dvList = df.columns.tolist()

    # セレクトボックス（独立変数）
    IndependentVariable = st.selectbox(
        '独立変数（群分け変数）※必ず２群にしてください',
        ivList)

    # 独立変数が２群になっているか確認
    ivLen = len(df[IndependentVariable].unique())
    ivType = df[IndependentVariable].dtypes

    if ivLen != 2:
        st.write(
            '<span style="color:red">独立変数が2群になっていないため、分析を実行できません。</span>',
            unsafe_allow_html=True)
    elif ivType != 'object':
        st.write(
            '<span style="color:red">独立変数が数値になっているため、分析を実行できません。</span>',
            unsafe_allow_html=True)
        st.write(
            '<span style="color:red">独立変数を文字列にして、再度アップロードしてください。</span>',
            unsafe_allow_html=True)
        st.write(
            '<span style="color:red">　例１）男性・女性</span>',
            unsafe_allow_html=True)
        st.write(
            '<span style="color:red">　例２）１年・２年</span>',
            unsafe_allow_html=True)
    else:
        st.write(
            '<span style="color:green">分析可能な独立変数です</span>',
            unsafe_allow_html=True)

    # 従属変数のリストから独立変数を削除（独立変数を従属変数に入れないため）
    dvList.remove(IndependentVariable)

    # 複数選択（従属変数）
    DependentVariable = st.multiselect(
        '従属変数（複数選択可）',
        dvList)

    st.write(
        '<span style="color:blue">【注意】従属変数に数値以外のものがある場合、分析できません</span>',
        unsafe_allow_html=True)

    # 確認ボタンの表示
    CHECK_btn = st.form_submit_button('確認')

# 分析前の確認フォーム
with st.form(key='check_form'):
    if CHECK_btn:
        # 独立変数から重複のないデータを抽出し、リストに変換
        DivideVariable = df[IndependentVariable].unique().tolist()

        st.subheader('【分析前の確認】')
        st.write(
            f'{IndependentVariable}'
            f'（{DivideVariable[0]}・{DivideVariable[1]}）によって')

        n = 0
        dvRangeView = len(DependentVariable)
        for dvListView in range(dvRangeView):
            st.write(f'● 'f'{(DependentVariable[n])}')
            n += 1
        st.write('　に有意な差が生まれるか検定します。')

    # 分析実行ボタンの表示
    TTEST_btn = st.form_submit_button('分析実行')

# 分析結果表示フォーム
with st.form(key='analyze_form'):
    if TTEST_btn:
        st.subheader('【分析結果】')
        st.write('【要約統計量】')
        # 独立変数の要素の数を取得
        dvRange = len(DependentVariable)

        # 各値の初期化
        n = 1
        summaryList = [DependentVariable]
        summaryColumns = ["有効N", "平均値", "中央値", "標準偏差", "分散",
                          "最小値", "最大値"]

        # 目的変数、従属変数から作業用データフレームのセット
        df00_list = [IndependentVariable]
        df00_list = df00_list + DependentVariable
        df00 = df[df00_list]

        # サマリ(df0)用のデータフレームのセット
        df0 = pd.DataFrame(index=summaryList, columns=summaryColumns)

        # サマリ(df0)用のデータフレームに平均値と標準偏差を追加
        for summary in range(dvRange):
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
        st.dataframe(df0)

        st.write('【平均値の差の検定】')

        DivideVariable = df00[IndependentVariable].unique().tolist()

        # 独立変数の要素の数を取得
        dvRange = len(DependentVariable)

        # 各値の初期化
        n = 1
        summaryList = [DependentVariable]

        # t検定結果用データフレーム（df1）の列を指定
        summaryColumns = ['全体M', '全体S.D', DivideVariable[0] + "M",
                          DivideVariable[0] + "S.D", DivideVariable[1] + "M",
                          DivideVariable[1] + "S.D", 'df', 't', 'p', 'sign',
                          'd']
        df1 = pd.DataFrame(index=summaryList, columns=summaryColumns)

        for summary in range(dvRange):
            # 列データの取得（nは従属変数の配列番号）
            y = df00.iloc[:, n]

            # df（元データ）男性でフィルターしたデータフレームをセット
            dv0 = df00[df00[IndependentVariable] == DivideVariable[0]]
            dv1 = df00[df00[IndependentVariable] == DivideVariable[1]]

            # フィルターした列データの取得（nは従属変数の配列番号）
            dv0y = dv0.iloc[:, n]
            dv1y = dv1.iloc[:, n]

            # t値、p値、s（全体標準偏差）、d値（効果量）の取得
            ttest = stats.ttest_ind(dv0y, dv1y, equal_var=False)
            t = abs(ttest[0])
            p = ttest[1]
            s = y.std()
            dv0ym = dv0y.mean()
            dv1ym = dv1y.mean()
            d_beta = dv0ym - dv1ym
            d = abs(d_beta) / s

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
            df1.at[df00.columns[n], '全体M'] = y.mean()
            df1.at[df00.columns[n], '全体S.D'] = y.std()
            df1.at[df00.columns[n], DivideVariable[0] + "M"] = dv0y.mean()
            df1.at[df00.columns[n], DivideVariable[0] + "S.D"] = dv0y.std()
            df1.at[df00.columns[n], DivideVariable[1] + "M"] = dv1y.mean()
            df1.at[df00.columns[n], DivideVariable[1] + "S.D"] = dv1y.std()
            df1.at[df00.columns[n], 'df'] = len(y) - 1
            df1.at[df00.columns[n], 't'] = t
            df1.at[df00.columns[n], 'p'] = p
            df1.at[df00.columns[n], 'sign'] = sign
            df1.at[df00.columns[n], 'd'] = d

            n += 1

        st.dataframe(df1)

        # サンプルサイズの取得
        sample_n = len(df00)
        sample_0 = len(dv0)
        sample_1 = len(dv1)

        st.write('【サンプルサイズ】')
        st.write(f'全体N ＝'f'{sample_n}')
        st.write(f'● {DivideVariable[0]}：'f'{sample_0}')
        st.write(f'● {DivideVariable[1]}：'f'{sample_1}')

        st.write('【分析結果の解釈】')

        # 各値の初期化、簡素化
        n = 0
        d0 = DivideVariable[0]
        d1 = DivideVariable[1]
        iv = IndependentVariable

        # sign の列番号を取得
        sign_n = df1.columns.get_loc('sign')
        # DivideVariable[0] + 'M' の列番号を取得
        d0n = df1.columns.get_loc(d0 + "M")
        # DivideVariable[1] + 'M' の列番号を取得
        d1n = df1.columns.get_loc(d1 + "M")

        for interpretation in range(dvRange):
            dn = DependentVariable[n]
            if df1.iat[n, sign_n] == "**":
                if df1.iat[n, d0n] > df1.iat[n, d1n]:
                    st.write(
                        f'{iv}によって【'f'{dn}】には有位な差が生まれる'f'（{d0}＞'f'{d1}）')
                elif df1.iat[n, d0n] < df1.iat[n, d1n]:
                    st.write(
                        f'{iv}によって【'f'{dn}】には有意な差が生まれる'f'（{d1}＞'f'{d0}）')
            elif df1.iat[n, sign_n] == "*":
                if df1.iat[n, d0n] > df1.iat[n, d1n]:
                    st.write(
                        f'{iv}によって【'f'{dn}】には有意な差が生まれる'f'（{d0}＞'f'{d1}）')
                elif df1.iat[n, d0n] < df1.iat[n, d1n]:
                    st.write(
                        f'{iv}によって【'f'{dn}】には有意な差が生まれる'f'（{d1}＞'f'{d0}）')
            elif df1.iat[n, sign_n] == "†":
                if df1.iat[n, d0n] > df1.iat[n, d1n]:
                    st.write(
                        f'{iv}によって【'f'{dn}】には有意な差が生まれる傾向にある'f'（{d0}＜'f'{d1}）')
                elif df1.iat[n, d0n] < df1.iat[n, d1n]:
                    st.write(
                        f'{iv}によって【'f'{dn}】には有意な差が生まれる傾向にある'f'（{d1}＜'f'{d0}）')
            elif df1.iat[n, sign_n] == "n.s.":
                st.write(f'{iv}によって【'f'{dn}】には有意な差が生まれない')

            n += 1

        TTEST_btn = st.form_submit_button('OK')

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
