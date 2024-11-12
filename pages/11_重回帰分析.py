import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from scipy import stats
import itertools
import matplotlib.pyplot as plt
import japanize_matplotlib
import networkx as nx
import matplotlib.patches as mpatches
import matplotlib.font_manager as font_manager

st.title("重回帰分析")
st.caption("Created by Dit-Lab.(Daiki Ito)")
st.write("")
st.write("説明変数と目的変数の関係を重回帰分析を使用して分析する補助を行います。")

st.write("")

uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])
use_demo_data = st.checkbox('デモデータを使用')

input_df = None
if use_demo_data:
    # TODO デモファイルを用意する
    input_df = pd.read_excel('multiple_regression_demo.xlsx', sheet_name=0)
elif uploaded_file is not None:
    if uploaded_file.type == 'text/csv':
        input_df = pd.read_csv(uploaded_file)
    else:
        input_df = pd.read_excel(uploaded_file)
        
if input_df is not None:
    st.subheader('元のデータ')
    st.write(input_df)

    numerical_cols = input_df.select_dtypes(exclude=['object', 'category']).columns.tolist()

    # 説明変数と目的変数の選択
    st.subheader("説明変数の選択")
    X_columns = st.multiselect("説明変数を選択してください", numerical_cols)
    st.subheader("目的変数の選択")
    y_columns = st.multiselect("目的変数を選択してください", [col for col in numerical_cols if col not in X_columns])
    
    st.subheader("【分析前の確認】")
    st.write(f"{X_columns}から{y_columns}の値を予測します。")
    
    # フォント設定（日本語対応）
    font_path = os.path.join(os.path.dirname(__file__), '..', 'ipaexg.ttf')  # フォントファイルへの正しいパス
    font_prop = font_manager.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    
    # 重回帰分析の実施
    if st.button('重回帰分析の実行'):
    
        if len(X_columns) > 0 and len(y_columns) > 0:
            X = input_df[X_columns]
            
            # 交互作用項の生成（総当たり）
            interaction_terms = []
            for i in range(2, len(X_columns) + 1):
                for combination in itertools.combinations(X_columns, i):
                    term = " × ".join(combination)
                    X[term] = X[list(combination)].prod(axis=1)
                    interaction_terms.append(term)
            
            X_poly_columns = X.columns
            
            # 結果をまとめるリストを初期化
            all_nodes = set()
            all_edges = []
            
            # 各目的変数の統計情報を保存する辞書を初期化
            dependent_var_stats = {}
            
            for y_column in y_columns:
                y = input_df[y_column]
                
                # 重回帰分析の実行
                model = LinearRegression()
                model.fit(X, y)
                
                # 結果の表示
                st.subheader(f"重回帰分析の結果：目的変数 {y_column}")
                r2 = r2_score(y, model.predict(X))
                
                # F値、自由度、p値の計算
                n = len(y)
                k = len(X_poly_columns)
                f_value = (r2 / k) / ((1 - r2) / (n - k - 1))
                df_model = k
                df_resid = n - k - 1
                p_value = stats.f.sf(f_value, df_model, df_resid)
                
                # 決定係数、F値、自由度、p値をデータフレームで表示
                summary_df = pd.DataFrame({
                    '指標': ['決定係数', 'F値', '自由度', 'p値'],
                    '値': [round(r2, 3), round(f_value, 3), f"({df_model}, {df_resid})", round(p_value, 4)]
                })
                st.write(summary_df)
                
                st.subheader("偏回帰係数と標準化係数")
                standardized_coef = model.coef_ * (X.std() / y.std())
                coefficients = pd.DataFrame({
                    "変数": X_poly_columns, 
                    "偏回帰係数": model.coef_, 
                    "標準化係数": standardized_coef
                })
                coefficients = coefficients.applymap(lambda x: round(x, 3) if isinstance(x, (int, float)) else x)
                st.write(coefficients)
                
                # 数理モデルの表示
                intercept = model.intercept_
                coefs = model.coef_
                equation_terms = [f"{round(coef, 3)} × {var}" for coef, var in zip(coefs, X_poly_columns)]
                equation = f"{y_column} = {round(intercept, 3)} + " + " + ".join(equation_terms)
                st.write("数理モデル：")
                st.write(equation)
                
                # p値に応じたアノテーション
                if p_value < 0.01:
                    p_annotation = 'p<0.01 **'
                elif p_value < 0.05:
                    p_annotation = 'p<0.05 *'
                elif p_value < 0.1:
                    p_annotation = 'p<0.1 †'
                else:
                    p_annotation = 'p≥0.1 n.s.'
                
                # 統計情報を保存
                dependent_var_stats[y_column] = {
                    'r2': r2,
                    'f_value': f_value,
                    'df_model': df_model,
                    'df_resid': df_resid,
                    'p_annotation': p_annotation
                }
                
                # 交互作用項を除外した変数リスト
                main_X_columns = X_columns
                
                # 標準化係数の取得（交互作用項を除外）
                main_coef_indices = [i for i, col in enumerate(X_poly_columns) if col in main_X_columns]
                main_standardized_coef = standardized_coef[main_coef_indices]
                main_X_poly_columns = [X_poly_columns[i] for i in main_coef_indices]
                
                # パス図の作成
                G = nx.DiGraph()
                
                # ノードの追加
                for var in main_X_poly_columns:
                    G.add_node(var)
                    all_nodes.add(var)
                G.add_node(y_column)
                all_nodes.add(y_column)
                
                # エッジの追加
                for idx, coef in zip(main_coef_indices, main_standardized_coef):
                    if abs(coef) >= 0.1:
                        if abs(coef) >= 0.2:
                            weight = 2  # 太い線
                        else:
                            weight = 1  # 細い線
                        G.add_edge(X_poly_columns[idx], y_column, weight=weight, label=round(coef, 2))
                        all_edges.append({
                            'from': X_poly_columns[idx],
                            'to': y_column,
                            'weight': weight,
                            'coef': round(coef, 2)
                        })
                
                # ノードの位置設定
                pos = {}
                num_X = len(main_X_poly_columns)
                for idx, var in enumerate(main_X_poly_columns):
                    pos[var] = (-1, idx)
                pos[y_column] = (1, num_X / 2)
                
                # 描画
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # ノードの描画（ノードサイズを変更しない）
                nx.draw_networkx_nodes(G, pos, node_color='lightgrey', node_shape='s', ax=ax)
                
                # ノードラベルの描画（角丸四角形の背景を設定）
                labels = {node: node for node in G.nodes()}
                nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, ax=ax,
                                        bbox=dict(boxstyle="round,pad=0.3", fc="lightgrey", ec="black"),
                                        font_family=font_prop.get_name())
                
                # エッジの描画（矢印を直線にする）
                edges = G.edges()
                weights = [G[u][v]['weight'] for u, v in edges]
                nx.draw_networkx_edges(G, pos, edgelist=edges, width=weights, arrows=True,
                                       arrowstyle='-|>', arrowsize=15, ax=ax)
                
                # エッジラベルの描画（標準化係数）
                edge_labels = nx.get_edge_attributes(G, 'label')
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, ax=ax,
                                             font_family=font_prop.get_name())
                
                # 目的変数の下にR値とF値、p値アノテーションを表示（位置を調整）
                x, y_pos = pos[y_column]
                ax.text(x, y_pos - 0.1, f"R={round(np.sqrt(r2),2)}\nF=({df_model},{df_resid})={round(f_value,2)}\n{p_annotation}",
                        horizontalalignment='center', verticalalignment='top', fontsize=10, fontproperties=font_prop)
                
                # 軸の非表示
                plt.axis('off')
                st.pyplot(fig)
                plt.close(fig)
            
            # まとめたパス図の作成
            st.subheader("まとめたパス図")
            G_combined = nx.DiGraph()
            
            # ノードの追加
            for node in all_nodes:
                G_combined.add_node(node)
            
            # エッジの追加
            for edge in all_edges:
                G_combined.add_edge(edge['from'], edge['to'], weight=edge['weight'], label=edge['coef'])
            
            # ノードの位置設定
            pos = {}
            # 説明変数を左側に配置
            for idx, var in enumerate(X_columns):
                pos[var] = (-1, idx)
            # 目的変数を右側に配置
            num_X = len(X_columns)
            num_Y = len(y_columns)
            spacing = num_X / (num_Y + 1)
            for idx, var in enumerate(y_columns):
                pos[var] = (1, spacing * (idx + 1))
            
            # 描画
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # ノードの描画（ノードサイズを変更しない）
            nx.draw_networkx_nodes(G_combined, pos, node_color='lightgrey', node_shape='s', ax=ax)
            
            # ノードラベルの描画（角丸四角形の背景を設定）
            labels = {node: node for node in G_combined.nodes()}
            nx.draw_networkx_labels(G_combined, pos, labels=labels, font_size=10, ax=ax,
                                    bbox=dict(boxstyle="round,pad=0.3", fc="lightgrey", ec="black"),
                                    font_family=font_prop.get_name())
            
            # エッジの描画（矢印を直線にする）
            edges = G_combined.edges()
            weights = [G_combined[u][v]['weight'] for u, v in edges]
            nx.draw_networkx_edges(G_combined, pos, edgelist=edges, width=weights, arrows=True,
                                   arrowstyle='-|>', arrowsize=15, ax=ax)
            
            # エッジラベルの描画（標準化係数）
            edge_labels = nx.get_edge_attributes(G_combined, 'label')
            nx.draw_networkx_edge_labels(G_combined, pos, edge_labels=edge_labels, font_size=10, ax=ax,
                                         font_family=font_prop.get_name())
            
            # 各目的変数の下にR値とF値、p値アノテーションを表示（位置を調整）
            for y_column in y_columns:
                if y_column in pos:
                    x, y_pos = pos[y_column]
                    dep_stats = dependent_var_stats[y_column]
                    r2 = dep_stats['r2']
                    f_value = dep_stats['f_value']
                    df_model = dep_stats['df_model']
                    df_resid = dep_stats['df_resid']
                    p_annotation = dep_stats['p_annotation']
                    ax.text(x, y_pos - 0.1, f"R={round(np.sqrt(r2),2)}\nF=({df_model},{df_resid})={round(f_value,2)}\n{p_annotation}",
                            horizontalalignment='center', verticalalignment='top', fontsize=10, fontproperties=font_prop)
            
            # 軸の非表示
            plt.axis('off')
            st.pyplot(fig)
            plt.close(fig)

st.write('')
st.write('')
st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
# Copyright
st.subheader('© 2022-2024 Dit-Lab.(Daiki Ito). All Rights Reserved.')
st.write("easyStat: Open Source for Ubiquitous Statistics")
st.write("Democratizing data, everywhere.")
st.write("")
st.subheader("In collaboration with our esteemed contributors:")
st.write("・Toshiyuki")
st.write("With heartfelt appreciation for their dedication and support.")
