import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import japanize_matplotlib

import common


st.set_page_config(page_title='探索的データ分析（EDA）', layout='wide')

st.title('探索的データ分析（EDA）')
common.display_header()
st.write('簡易的な探索的データ分析（EDA）が実行できます')
st.write('')

# ファイルアップローダー
uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('datasets/eda_demo.xlsx', sheet_name=0)
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
    # カテゴリ変数と数値変数の選択
    cols = df.columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    numerical_cols = df.select_dtypes(exclude=['object', 'category']).columns.tolist()

    # 要約統計量表示
    st.subheader('要約統計量')
    summary_df = df.describe(include='all').transpose()
    st.write(summary_df)

    # 可視化
    st.subheader('可視化')

    # カテゴリ変数の可視化
    for col in categorical_cols:
        # 並び替えのオプションを選択
        sort_order = st.selectbox(
            f'【{col}】 の並び替え順を選択してください',
            ('度数', '名前順'),
            key=col
        )

        value_counts = df[col].value_counts()

        # 選択された並び替え順に基づいてデータを並び替え
        if sort_order == '名前順':
            value_counts = value_counts.sort_index()
        else:
            value_counts = value_counts.sort_values(ascending=False)

        fig = px.bar(
            x=value_counts.index,
            y=value_counts.values,
            labels={'x': col, 'y': 'Count'},
            title=f'【{col}】 の可視化 （{sort_order}）'
        )
        fig.update_layout(bargap=0.2)
        st.plotly_chart(fig)

    # 数値変数の可視化
    for col in numerical_cols:
        fig = px.histogram(df, x=col, title=f'【{col}】 の可視化（ヒストグラム）')
        fig.update_layout(bargap=0.2)
        st.plotly_chart(fig)
        fig = px.box(df, x=col, title=f'【{col}】 の可視化（箱ひげ図）')
        st.plotly_chart(fig)

    # アップロードされたデータセットに数値変数が含まれている場合
    if numerical_cols:
        st.subheader('選択した数値変数の可視化（箱ひげ図）')
        selected_num_cols = st.multiselect(
            '数値変数を選択してください', 
            numerical_cols, 
            default=numerical_cols
        )
        fig = px.box(df, x=selected_num_cols, points='all', title='選択した数値変数の可視化')
        st.plotly_chart(fig)

    st.subheader('選択した２変数の可視化')
    
    # 変数選択
    selected_vars = st.multiselect('変数を２つ選択してください:', df.columns.tolist(), max_selections=2)

    if len(selected_vars) > 2:
        st.error('2項目以上を選択することはできません。選択をクリアし、2項目のみを選択してください。')
    elif len(selected_vars) == 2:
        var1, var2 = selected_vars
     
        # カテゴリ×カテゴリ
        if var1 in categorical_cols and var2 in categorical_cols:
            cross_tab = pd.crosstab(df[var1], df[var2])
            fig = px.imshow(
                cross_tab,
                labels=dict(color='Count'),
                title=f'度数： 【{var1}】 × 【{var2}】'
            )
            st.plotly_chart(fig)

        # 数値×数値
        elif var1 in numerical_cols and var2 in numerical_cols:
            fig = px.scatter(df, x=var1, y=var2, title=f'散布図： 【{var1}】 × 【{var2}】')
            st.plotly_chart(fig)
            st.write(f'相関係数： {df[var1].corr(df[var2]):.2f}')
        
        # カテゴリ×数値
        else:
            if var1 in categorical_cols:
                cat_var, num_var = var1, var2
            else:
                cat_var, num_var = var2, var1
            
            fig = px.box(df, x=cat_var, y=num_var, title=f'箱ひげ図： 【{cat_var}】 × 【{num_var}】')
            st.plotly_chart(fig)
    
    st.subheader('２つのカテゴリ変数と１つの数値変数による棒グラフ')

    # カテゴリ変数と数値変数の選択
    cat_vars = st.multiselect(
        '２つのカテゴリ変数を選択してください:', 
        categorical_cols, 
        key='cat_vars',
        max_selections=2
    )
    num_var = st.selectbox('１つの数値変数を選択してください:', numerical_cols, key='num_var')

    if len(cat_vars) == 2 and num_var:
        cat_var1, cat_var2 = cat_vars

        # データの準備
        grouped_df = df.groupby([cat_var1, cat_var2])[num_var].mean().reset_index()

        # 棒グラフの作成
        fig = px.bar(
            grouped_df,
            x=cat_var1,
            y=num_var,
            color=cat_var2,
            facet_col=cat_var2,
            labels={num_var: 'AVE: ' + num_var, cat_var1: cat_var1, cat_var2: cat_var2},
            title=f'【{cat_var1}】 と 【{cat_var2}】 による 【{num_var}】 の比較'
        )
        # グラフのレイアウトを更新
        fig.update_layout(
            xaxis_title=cat_var1,
            yaxis_title=f'AVE:  {num_var}',
            margin=dict(l=0, r=0, t=60, b=0),
        )

        st.plotly_chart(fig)
    else:
        st.warning('２つのカテゴリ変数と１つの数値変数を選択してください。')

# フッター
common.display_copyright()
common.display_special_thanks()
