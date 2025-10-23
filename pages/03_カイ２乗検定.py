import japanize_matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import scipy.stats as stats
import streamlit as st
from PIL import Image

import common


st.set_page_config(page_title="カイ２乗分析", layout="wide")

st.title("カイ２乗分析")
common.display_header()
st.write("２つの変数からクロス表やヒートマップを出力し、度数の偏りを解釈する補助を行います。")
st.write("")

# AI解釈機能の設定
gemini_api_key, enable_ai_interpretation = common.AIStatisticalInterpreter.setup_ai_sidebar()

# 分析のイメージ
image = Image.open('images/chi_square.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('datasets/chi_square_demo.xlsx', sheet_name=0)
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

    # カテゴリ変数が存在するかチェック
    if len(categorical_cols) == 0:
        st.error('エラー: データにカテゴリ変数が含まれていません。カテゴリ変数（文字列型）のデータをアップロードしてください。')
    elif len(categorical_cols) < 2:
        st.warning(f'警告: カテゴリ変数が1つしかありません（{categorical_cols[0]}）。カイ二乗検定には2つ以上のカテゴリ変数が必要です。')
    else:
        # カテゴリ変数の選択
        st.subheader("カテゴリ変数の選択")
        selected_col1 = st.selectbox('変数1を選択してください', categorical_cols, key='select1')
        # categorical_cols.remove(selected_col1)  # 選択済みの変数をリストから削除
        selected_col2 = st.selectbox('変数2を選択してください', categorical_cols, key='select2')

        # 同じ変数が選択されていないかチェック
        if selected_col1 == selected_col2:
            st.warning('警告: 同じ変数が選択されています。異なる変数を選択してください。')
        else:
            # 選択した変数の度数分布のバープロット
            st.subheader(f'【{selected_col1}】 と 【{selected_col2}】 の度数分布')

            # クロス表の作成
            try:
                crosstab = pd.crosstab(df[selected_col1], df[selected_col2])

                # クロス表が空でないかチェック
                if crosstab.empty or crosstab.sum().sum() == 0:
                    st.error('エラー: クロス表が空です。データに有効な値が含まれていることを確認してください。')
                else:
                    # クロス表を長い形式に変換
                    crosstab_long = crosstab.reset_index().melt(id_vars=selected_col1, value_name='度数')

                    # プロットの作成
                    fig = px.bar(
                        crosstab_long,
                        x=selected_col2,
                        y='度数',
                        color=selected_col1,
                        barmode='group',
                        labels={selected_col1: selected_col1, selected_col2: selected_col2, '度数': '度数'},
                        title=f'【{selected_col1}】 と 【{selected_col2}】 の度数分布'
                    )

                    # グラフの表示
                    st.plotly_chart(fig)

                    # クロス表の作成と表示
                    st.subheader(f'【{selected_col1}】 と 【{selected_col2}】 のクロス表')

                    # カイ２乗検定の実行
                    try:
                        chi2, p_value, dof, expected = stats.chi2_contingency(crosstab)

                        # 期待度数のデータフレームの作成
                        expected_df = pd.DataFrame(expected, columns=crosstab.columns, index=crosstab.index)
                        expected_df = expected_df.round(2)  # 小数点第2位で四捨五入

                        # (観測度数 - 期待度数)^2 / 期待度数 の計算
                        chi_square_value_df = ((crosstab - expected) ** 2) / expected
                        chi_square_value_df = chi_square_value_df.round(2)  # 小数点第2位で四捨五入

                        # 有意差を確認するための残差の計算
                        residuals = (crosstab - expected) / np.sqrt(expected)

                        # 有意水準0.05でのz値の閾値
                        threshold = stats.norm.ppf(1 - 0.05 / 2)

                        # 有意に差が出ているセルのマスキング
                        mask_significant = residuals.abs() > threshold

                        # セルに色を付ける
                        colors = mask_significant.applymap(lambda x: 'background-color: yellow' if x else '')

                        # データフレームを表示
                        st.subheader('データフレームの表示')

                        st.write('＜観測度数＞')
                        # 合計の行と列を追加
                        crosstab['合計'] = crosstab.sum(axis=1)  # 行の合計
                        crosstab.loc['合計'] = crosstab.sum()  # 列の合計
                        st.write(crosstab.style.apply(lambda x: colors, axis=None))

                        st.write('＜期待度数＞')
                        st.write(expected_df.style.apply(lambda x: colors, axis=None).format("{:.2f}"))

                        st.write('＜カイ二乗値＞')
                        st.caption('(観測度数 - 期待度数)^2 / 期待度数')
                        st.write(chi_square_value_df.style.apply(lambda x: colors, axis=None).format("{:.2f}"))

                        st.caption('有意に差が出ているセルは黄色で表示されます:')

                        # カイ二乗検定の結果を表示
                        st.subheader('カイ二乗検定の結果')
                        st.write(f'カイ二乗統計量: {chi2:.2f}')
                        st.write(f'P値: {p_value:.2f}')

                        # ヒートマップの作成（合計を除く）
                        fig_heatmap = px.imshow(
                            crosstab.iloc[:-1, :-1],  # 合計の行と列を除外
                            labels=dict(x=selected_col2, y=selected_col1, color='観測度数'),
                            title=f'【{selected_col1}】 と 【{selected_col2}】 の観測度数ヒートマップ'
                        )

                        # アノテーションの追加 (観測度数をセルに表示)
                        annotations = []
                        for i, row in enumerate(crosstab.iloc[:-1, :-1].values):
                            for j, value in enumerate(row):
                                annotations.append({
                                    'x': j,
                                    'y': i,
                                    'xref': 'x',
                                    'yref': 'y',
                                    'text': f"{value:.0f}",
                                    'showarrow': False,
                                    'font': {
                                        'color': 'black'
                                    }
                                })

                        # ヒートマップに観測度数を表示
                        fig_heatmap.update_layout(annotations=annotations)
                        fig_heatmap.update_layout(scene=dict(aspectmode="manual", aspectratio=dict(x=1, y=1, z=0.05)))

                        # ヒートマップの表示
                        st.plotly_chart(fig_heatmap)

                        # AI解釈機能の追加
                        if gemini_api_key and enable_ai_interpretation:
                            # 結果をまとめる
                            chi_square_results = {
                                'chi2': chi2,
                                'p_value': p_value,
                                'dof': dof,
                                'var1': selected_col1,
                                'var2': selected_col2,
                                'crosstab': crosstab.iloc[:-1, :-1],  # 合計行・列を除く
                                'expected': expected_df
                            }

                            # AI解釈を表示
                            common.AIStatisticalInterpreter.display_ai_interpretation(
                                api_key=gemini_api_key,
                                enabled=enable_ai_interpretation,
                                results=chi_square_results,
                                analysis_type='chi_square',
                                key_prefix=f'chi_square_{selected_col1}_{selected_col2}'
                            )

                    except ValueError as e:
                        st.error(f'エラー: カイ二乗検定の実行中にエラーが発生しました。\n詳細: {str(e)}\n\n期待度数が小さすぎる可能性があります（各セルの期待度数が5以上必要）。')
                    except Exception as e:
                        st.error(f'エラー: 予期しないエラーが発生しました。\n詳細: {str(e)}')

            except KeyError as e:
                st.error(f'エラー: 選択された変数がデータに存在しません。\n詳細: {str(e)}')
            except Exception as e:
                st.error(f'エラー: クロス表の作成中にエラーが発生しました。\n詳細: {str(e)}')

# フッター
common.display_copyright()
common.display_special_thanks()

