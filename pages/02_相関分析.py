import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from PIL import Image
from scipy import stats

import common


st.set_page_config(page_title='相関分析', layout='wide')

st.title('相関分析')
common.display_header()

# 学習支援機能の統合
learning_assistant = common.StatisticalLearningAssistant()
learning_assistant.check_learning_progress("相関分析")

# 学習レベル選択
level = st.selectbox("学習レベルを選択してください", 
                     ["beginner", "intermediate", "advanced"],
                     format_func=lambda x: {"beginner": "初級者", "intermediate": "中級者", "advanced": "上級者"}[x])

# 概念説明
learning_assistant.show_concept_explanation('correlation', level)

# インタラクティブガイド
common.show_interactive_guide('correlation')

st.write('２つの変数から相関係数を表やヒートマップで出力し、相関関係の解釈の補助を行います。')
st.write('')

# 分析のイメージ
image = Image.open('images/correlation.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
validator = common.StatisticalValidator()
df = None

if use_demo_data:
    try:
        df = pd.read_excel('datasets/correlation_demo.xlsx', sheet_name=0)
        st.success("✅ デモデータを読み込みました")
        st.write(df.head())
    except Exception as e:
        st.error(f"⚠️ デモデータの読み込みに失敗しました: {e}")
else:
    if uploaded_file is not None:
        df = validator.safe_file_load(uploaded_file)
        if df is not None:
            st.success("✅ ファイルを正常に読み込みました")
            st.write(df.head())

if df is not None:
    # 基本的なデータ検証
    if not validator.validate_sample_size(df, min_size=5, analysis_type="相関分析"):
        st.stop()
    
    # 数値変数の抽出
    numerical_cols = df.select_dtypes(exclude=['object', 'category']).columns.tolist()
    
    if len(numerical_cols) < 2:
        st.error("⚠️ 相関分析には最低2つの数値変数が必要です。")
        st.info("💡 **解決方法:** データクレンジングページで変数を数値型に変換してください。")
        st.stop()
    
    # 数値変数の選択
    st.subheader('数値変数の選択')
    selected_cols = st.multiselect('数値変数を選択してください', numerical_cols)
    
    if len(selected_cols) < 2:
        st.warning('少なくとも2つの変数を選択してください。')
    else:
        # データ型の検証
        if not validator.validate_data_types(df, selected_cols, 'numeric'):
            st.stop()
        
        # 欠損値のチェック
        missing_info = validator.check_missing_values(df, selected_cols)
        
        # 欠損値がある場合は除外して継続
        clean_df = df[selected_cols].dropna()
        if len(clean_df) < len(df):
            removed_rows = len(df) - len(clean_df)
            st.info(f"📋 欠損値のある{removed_rows}行を除外して分析を実行します。")
        
        if len(clean_df) < 3:
            st.error("⚠️ 欠損値を除外した結果、十分なデータがありません。")
            st.stop()
        # 相関マトリックスの計算
        try:
            corr_matrix = clean_df.corr()
            
            # 有意性検定の実行（2変数の場合）
            if len(selected_cols) == 2:
                var1, var2 = selected_cols
                r_value = corr_matrix.iloc[0, 1]
                # ピアソンの相関係数の有意性検定
                correlation_coef, p_value = stats.pearsonr(clean_df[var1], clean_df[var2])
                
                st.subheader('🔍 詳細な相関分析結果')
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("相関係数 (r)", f"{r_value:.3f}")
                with col2:
                    st.metric("p値", f"{p_value:.3f}")
                with col3:
                    significance = "有意" if p_value < 0.05 else "非有意"
                    st.metric("有意性 (α=0.05)", significance)
                
                # 結果解釈の表示
                interpreter = common.ResultInterpreter()
                interpretation = interpreter.interpret_correlation(r_value, p_value)
                st.markdown(interpretation)
            
            # 相関マトリックスの表示
            st.subheader('相関マトリックス')
            st.dataframe(corr_matrix.round(3))
            
        except Exception as e:
            st.error(f"⚠️ 相関分析の計算中にエラーが発生しました: {e}")
            st.info("💡 **確認事項:**\n- 選択した変数がすべて数値型か\n- データに十分な値が含まれているか")
            st.stop()
        
        # ヒートマップの表示
        try:
            fig_heatmap = px.imshow(
                corr_matrix, 
                color_continuous_scale='rdbu', 
                labels=dict(color='相関係数'),
                aspect='auto'
            )
            
            # アノテーションの追加
            annotations = []
            for i, row in enumerate(corr_matrix.values):
                for j, value in enumerate(row):
                    if not np.isnan(value):  # NaN値をチェック
                        annotations.append({
                            'x': j,
                            'y': i,
                            'xref': 'x',
                            'yref': 'y',
                            'text': f'{value:.2f}',
                            'showarrow': False,
                            'font': {
                                'color': 'black' if -0.5 < value < 0.5 else 'white'
                            }
                        })
            fig_heatmap.update_layout(title='相関係数のヒートマップ', annotations=annotations)
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
        except Exception as e:
            st.error(f"⚠️ ヒートマップの作成中にエラーが発生しました: {e}")
            st.info("💡 基本的な相関マトリックスは上記の表をご確認ください。")

        # 散布図行列の作成
        st.subheader('散布図行列')
        
        # Plotlyで散布図行列を作成
        fig = make_subplots(
            rows=len(selected_cols), 
            cols=len(selected_cols),
            subplot_titles=['' for _ in range(len(selected_cols) * len(selected_cols))]
        )

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
            title='散布図行列とヒストグラム'
        )
        
        # 軸ラベルの追加
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

# フッター
common.display_copyright()
common.display_special_thanks()
