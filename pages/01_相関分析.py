import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import japanize_matplotlib
from PIL import Image

st.set_page_config(page_title="相関分析", layout="wide")

st.title("相関分析ウェブアプリ")

st.write("相関係数のヒートマップを生成し、相関の強さを視覚的に確認できます。")

# 分析のイメージ
image = Image.open('correlation.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('correlation_demo.xlsx', sheet_name=0)
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
    # 数値変数の抽出
    numerical_cols = df.select_dtypes(exclude=['object', 'category']).columns.tolist()

    # 数値変数の選択
    st.subheader("数値変数の選択")
    selected_cols = st.multiselect('数値変数を選択してください', numerical_cols, default=numerical_cols)
    
    if len(selected_cols) < 2:
        st.write('少なくとも2つの変数を選択してください。')
    else:
        # 相関マトリックスの計算
        corr_matrix = df[selected_cols].corr()
        
        # 相関マトリックスの表示
        st.subheader('相関マトリックス')
        st.dataflame(corr_matrix)
        
        # ヒートマップの表示
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
        st.pyplot(fig)
        
        # 相関の解釈
        st.subheader('相関の解釈:')
        for i, col1 in enumerate(selected_cols):
            for j, col2 in enumerate(selected_cols):
                if i < j:
                    correlation = corr_matrix.loc[col1, col2]
                    description = f'{col1}と{col2}は'
                    if correlation > 0.7:
                        description += f'強い正の相関がある (r={correlation:.2f})'
                    elif correlation > 0.3:
                        description += f'中程度の正の相関がある (r={correlation:.2f})'
                    elif correlation > -0.3:
                        description += f'ほとんど相関がない (r={correlation:.2f})'
                    elif correlation > -0.7:
                        description += f'中程度の負の相関がある (r={correlation:.2f})'
                    else:
                        description += f'強い負の相関がある (r={correlation:.2f})'
                    st.write(description)



st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')