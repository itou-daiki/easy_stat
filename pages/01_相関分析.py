import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import japanize_matplotlib
from PIL import Image

st.set_page_config(page_title="相関分析", layout="wide")

st.title("相関分析ウェブアプリ")

st.write("このウェブアプリケーションでは、アップロードしたデータセットの特定の変数間の相関分析を簡単に実行できます。\
          さらに、相関係数のヒートマップを生成し、相関の強さを視覚的に確認できます。")

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

if uploaded_file is not None:
    if uploaded_file.type == 'text/csv':
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # 数値変数の選択
    numerical_cols = df.select_dtypes(exclude=['object', 'category']).columns.tolist()
    if numerical_cols:
        selected_vars = st.multiselect('数値変数を選択してください:', numerical_cols)
        if selected_vars:
            sub_df = df[selected_vars]
            
            # 相関マトリックスの計算
            correlation_matrix = sub_df.corr()
            
            # データフレームとして相関マトリックスを表示
            st.subheader('相関マトリックス')
            st.write(correlation_matrix)
            
            # ヒートマップの表示
            st.subheader('ヒートマップ')
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', ax=ax)
            st.pyplot(fig)
            
            # 分析結果の解釈
            st.subheader('分析結果の解釈')
            for v1 in selected_vars:
                for v2 in selected_vars:
                    if v1 != v2:
                        r = round(correlation_matrix.loc[v1, v2], 2)
                        if 0.7 <= r <= 1.0:
                            st.markdown(f'&#8203;``【oaicite:13】``&#8203;と&#8203;``【oaicite:12】``&#8203;の間には「強い正の相関」がある（ r = {r} )')
                        elif 0.4 <= r < 0.7:
                            st.markdown(f'&#8203;``【oaicite:11】``&#8203;と&#8203;``【oaicite:10】``&#8203;の間には「正の相関」がある（ r = {r} )')
                        elif 0.2 <= r < 0.4:
                            st.markdown(f'&#8203;``【oaicite:9】``&#8203;と&#8203;``【oaicite:8】``&#8203;の間には「弱い正の相関」がある（ r = {r} )')
                        elif -0.2 <= r < 0.2:
                            st.write(f'&#8203;``【oaicite:7】``&#8203;と&#8203;``【oaicite:6】``&#8203;の間には「相関がない」（ r = {r} )')
                        elif -0.4 <= r < -0.2:
                            st.markdown(f'&#8203;``【oaicite:5】``&#8203;と&#8203;``【oaicite:4】``&#8203;の間には「弱い負の相関」がある（ r = {r} )')
                        elif -0.7 <= r < -0.4:
                            st.markdown(f'&#8203;``【oaicite:3】``&#8203;と&#8203;``【oaicite:2】``&#8203;の間には「負の相関」がある（ r = {r} )')
                        elif -1.0 <= r < -0.7:
                            st.markdown(f'&#8203;``【oaicite:1】``&#8203;と&#8203;``【oaicite:0】``&#8203;の間には「強い負の相関」がある（ r = {r} )')
        else:
            st.warning('少なくとも1つの数値変数を選択してください。')
    else:
        st.error('アップロードされたデータセットに数値変数は含まれていません。')
else:
    st.warning('データセットをアップロードしてください。')

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')