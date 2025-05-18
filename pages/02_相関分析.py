import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import japanize_matplotlib
from PIL import Image
import seaborn as sns
import numpy as np
import common


st.set_page_config(page_title="相関分析", layout="wide")
st.title("相関分析")
common.display_header()
st.write("２つの変数から相関係数を表やヒートマップで出力し、相関関係の解釈の補助を行います。")
st.write("")

# 分析のイメージ
image = Image.open('images/correlation.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('datasets/correlation_demo.xlsx', sheet_name=0)
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
    selected_cols = st.multiselect('数値変数を選択してください', numerical_cols)
    
    if len(selected_cols) < 2:
        st.write('少なくとも2つの変数を選択してください。')
    else:
        # 相関マトリックスの計算
        corr_matrix = df[selected_cols].corr()
        
        # 相関マトリックスの表示
        st.subheader('相関マトリックス')
        st.dataframe(corr_matrix)
        
        # ヒートマップの表示
        fig_heatmap = px.imshow(corr_matrix, 
                               color_continuous_scale='rdbu', 
                               labels=dict(color="相関係数"))
        
        # アノテーションの追加
        annotations = []
        for i, row in enumerate(corr_matrix.values):
            for j, value in enumerate(row):
                annotations.append({
                    'x': j,
                    'y': i,
                    'xref': 'x',
                    'yref': 'y',
                    'text': f"{value:.2f}",
                    'showarrow': False,
                    'font': {
                        'color': 'black' if -0.5 < value < 0.5 else 'white'
                    }
                })
        fig_heatmap.update_layout(title="相関係数のヒートマップ", annotations=annotations)
        st.plotly_chart(fig_heatmap)

        # 散布図行列の作成
        st.subheader('散布図行列')
        
        # Plotlyで散布図行列を作成
        fig = make_subplots(rows=len(selected_cols), 
                           cols=len(selected_cols),
                           subplot_titles=['' for _ in range(len(selected_cols) * len(selected_cols))])

        # ヒストグラムと散布図の作成
        for i, var1 in enumerate(selected_cols):
            for j, var2 in enumerate(selected_cols):
                row = i + 1
                col = j + 1
                
                if i == j:  # 対角線上にヒストグラムを配置
                    fig.add_trace(
                        go.Histogram(x=df[var1], name=var1),
                        row=row, col=col
                    )
                else:  # 散布図を配置
                    fig.add_trace(
                        go.Scatter(
                            x=df[var2],
                            y=df[var1],
                            mode='markers',
                            marker=dict(size=6),
                            showlegend=False
                        ),
                        row=row, col=col
                    )

        # レイアウトの調整
        fig.update_layout(
            height=200 * len(selected_cols),
            width=200 * len(selected_cols),
            showlegend=False,
            title="散布図行列とヒストグラム"
        )
        
        # 軸ラベルの追加 (修正部分)
        for i, var1 in enumerate(selected_cols):
            for j, var2 in enumerate(selected_cols):
                # 横軸のラベルを最下の行のみに設定
                if i == len(selected_cols) - 1:  
                    fig.update_xaxes(title_text=var2, row=i+1, col=j+1)
                else:
                    fig.update_xaxes(title_text='', row=i+1, col=j+1)
        
                # 縦軸のラベルを最左の列のみに設定
                if j == 0:  
                    fig.update_yaxes(title_text=var1, row=i+1, col=j+1)
                else:
                    fig.update_yaxes(title_text='', row=i+1, col=j+1)

        st.plotly_chart(fig)
        
        # 相関の解釈
        st.subheader('解釈の補助')
        for i, col1 in enumerate(selected_cols):
            for j, col2 in enumerate(selected_cols):
                if i < j:
                    correlation = corr_matrix.loc[col1, col2]
                    description = f'【{col1}】と【{col2}】には'
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

# Copyright
common.display_copyright()
common.display_special_thanks()