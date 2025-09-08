import itertools
import os
import json
import requests

import matplotlib.font_manager as font_manager
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import japanize_matplotlib
import networkx as nx
import numpy as np
import pandas as pd
import statsmodels.api as sm
import streamlit as st
from scipy import stats
from sklearn.metrics import r2_score

import common


common.set_font()

def call_gemini_api(api_key, prompt):
    """Gemini 2.0 Flash APIを呼び出す関数"""
    if not api_key:
        return "APIキーが設定されていません。"
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    headers = {
        "Content-Type": "application/json",
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048,
        }
    }
    
    try:
        response = requests.post(f"{url}?key={api_key}", headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "APIからの応答が予期しない形式です。"
        else:
            return f"APIエラー: {response.status_code} - {response.text}"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

def create_statistics_interpretation_prompt(coefficients_df, summary_df, equation, y_column):
    """統計指標の解釈プロンプトを作成"""
    prompt = f"""
あなたは統計分析の専門家です。以下の重回帰分析の結果を読み取り、統計指標の意味と変数間の関係性について日本語で詳しく解釈・考察してください。

【分析対象】
目的変数: {y_column}

【回帰係数の結果】
{coefficients_df.to_string(index=False)}

【統計指標】
{summary_df.to_string(index=False)}

【数理モデル】
{equation}

【解釈・考察してほしい内容】
1. 決定係数(R²)の値から見たモデルの説明力
2. F値とp値から見た回帰式全体の有意性
3. 各説明変数の偏回帰係数と標準化係数の解釈
4. 各変数のp値から見た統計的有意性の判断
5. 変数間の関係性の強さと方向性
6. 実際の業務や研究での活用方法の提案
7. モデルの限界や注意点

統計の専門知識がない人にも分かりやすく、具体的で実践的な解釈を提供してください。
"""
    return prompt

def create_comprehensive_interpretation_prompt(all_results, X_columns, y_columns):
    """包括的な変数間関係性の解釈プロンプトを作成"""
    # すべての結果をまとめたテキストを構築
    results_summary = ""
    for y_col, result_data in all_results.items():
        results_summary += f"\n【目的変数: {y_col}】\n"
        results_summary += f"回帰係数:\n{result_data['coefficients'].to_string(index=False)}\n"
        results_summary += f"統計指標:\n{result_data['summary'].to_string(index=False)}\n"
        results_summary += f"数理モデル: {result_data['equation']}\n"
    
    prompt = f"""
あなたは統計分析の専門家です。以下の重回帰分析の包括的な結果から、変数間の複雑な関係性とシステム全体の構造について深く解釈・考察してください。

【分析概要】
説明変数: {', '.join(X_columns)}
目的変数: {', '.join(y_columns)}

【全分析結果】
{results_summary}

【包括的な解釈・考察してほしい内容】
1. 変数システム全体の構造分析
   - 各説明変数がどの目的変数に最も強く影響するか
   - 説明変数間の相対的な重要度比較
   
2. 変数間関係のパターン分析
   - 一貫性のある影響パターンの発見
   - 目的変数間での説明変数の影響の違い
   
3. 多重共線性や交互作用の可能性
   - 説明変数間の関係性の推測
   - 隠れた交互作用効果の示唆
   
4. システム的な解釈
   - ビジネスや研究文脈での変数関係の意味
   - 因果関係の可能性と限界
   
5. 実践的な活用戦略
   - 最も効果的な介入ポイント
   - 予測精度向上のための提案
   - リスク管理の観点
   
6. 分析の限界と改善提案
   - 現在のモデルの制約
   - 追加すべきデータや変数の提案
   - より高度な分析手法の推奨

統計の専門知識がない人にも理解できるよう、具体例を交えながら実践的で洞察に富んだ解釈を提供してください。
"""
    return prompt

st.title("重回帰分析")
common.display_header()
st.write("")
st.write("因果を推定した「複数の説明変数と目的変数」の関係を分析し、可視化を行います。")

# AI解釈機能の設定
st.sidebar.subheader("🤖 AI統計解釈機能")
st.sidebar.write("Gemini 2.0 Flash APIを使用して統計結果を自動解釈します")
gemini_api_key = st.sidebar.text_input("Gemini APIキーを入力してください", type="password", help="Google AI Studio (https://aistudio.google.com/) でAPIキーを取得できます")
enable_ai_interpretation = st.sidebar.checkbox("AI解釈機能を有効にする", disabled=not gemini_api_key)

if gemini_api_key and enable_ai_interpretation:
    st.sidebar.success("✅ AI解釈機能が有効になりました")
elif enable_ai_interpretation and not gemini_api_key:
    st.sidebar.error("❌ APIキーを入力してください")

st.write("")

uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])
use_demo_data = st.checkbox('デモデータを使用')

input_df = None
if use_demo_data:
    input_df = pd.read_excel('datasets/multiple_regression_demo.xlsx', sheet_name=0)
elif uploaded_file is not None:
    if uploaded_file.type == 'text/csv':
        input_df = pd.read_csv(uploaded_file)
    else:
        input_df = pd.read_excel(uploaded_file)
        
if input_df is not None:
    st.subheader('元のデータ')
    st.write(input_df)

    numerical_cols = input_df.select_dtypes(include=[np.number]).columns.tolist()

    # 説明変数と目的変数の選択
    st.subheader("説明変数の選択")
    X_columns = st.multiselect("説明変数を選択してください", numerical_cols, key='X_columns')
    st.subheader("目的変数の選択")
    y_columns = st.multiselect("目的変数を選択してください", [col for col in numerical_cols if col not in X_columns], key='y_columns')
    
    st.subheader("【分析前の確認】")
    st.write(f"{X_columns}から{y_columns}の値を予測します。")
       
    # 重回帰分析の実施
    if st.button('重回帰分析の実行'):
    
        if len(X_columns) > 0 and len(y_columns) > 0:
            X = input_df[X_columns].copy()
            
            # 交互作用項の生成（総当たり）
            interaction_terms = []
            for i in range(2, len(X_columns) + 1):
                for combination in itertools.combinations(X_columns, i):
                    term = " × ".join(combination)
                    X[term] = X[list(combination)].prod(axis=1)
                    interaction_terms.append(term)
            
            # すべての説明変数（交互作用項を含む）
            X_all_columns = X.columns.tolist()
            
            # 結果をまとめるリストを初期化
            all_nodes = set()
            all_edges = []
            
            # 各目的変数の統計情報を保存する辞書を初期化
            dependent_var_stats = {}
            
            # AI解釈用の全結果を保存する辞書を初期化
            all_analysis_results = {}
            
            for y_column in y_columns:
                y = input_df[y_column]
                
                # 元のデータで回帰分析（偏回帰係数用）
                X_with_const = sm.add_constant(X)
                model = sm.OLS(y, X_with_const).fit()
                
                # 偏回帰係数の取得
                unstandardized_coefs = model.params.values
                
                # 標準偏差の取得
                X_std = X.std()
                y_std = y.std()
                
                # 標準化係数の計算（定数項は除外）
                standardized_coefs = unstandardized_coefs[1:] * (X_std / y_std)
                
                # 偏回帰係数と標準化係数をデータフレームにまとめる
                coefficients = pd.DataFrame({
                    "変数": X_with_const.columns,
                    "偏回帰係数": unstandardized_coefs,
                    "標準化係数": np.insert(standardized_coefs.values, 0, np.nan)  # 定数項にnanを挿入
                })
                
                coefficients['p値'] = model.pvalues.values
                
                # 有意判定の追加
                def significance(p):
                    if p < 0.01:
                        return '**'
                    elif p < 0.05:
                        return '*'
                    elif p < 0.1:
                        return '†'
                    else:
                        return 'n.s.'
                coefficients['Sign'] = coefficients['p値'].apply(significance)
                
                # 'const'（定数項）を削除
                coefficients = coefficients[coefficients['変数'] != 'const']
                
                # インデックスをリセットして、行番号を非表示に
                coefficients = coefficients.reset_index(drop=True)
                
                # 実数を小数点第2位まで表示、整数はそのまま
                def format_numbers(x):
                    if pd.isnull(x):
                        return ''
                    elif isinstance(x, float):
                        return f"{x:.2f}"
                    else:
                        return x
                coefficients = coefficients.applymap(format_numbers)
                
                # データフレームを表示（行番号を非表示）
                st.subheader(f"重回帰分析の結果：目的変数 {y_column}")
                st.dataframe(coefficients)
                
                # 決定係数、F値、自由度、p値を取得
                r2 = model.rsquared
                f_value = model.fvalue
                df_model = int(model.df_model)
                df_resid = int(model.df_resid)
                p_value = model.f_pvalue
                
                # 統計量を表示（実数は小数点第2位まで）
                summary_df = pd.DataFrame({
                    '指標': ['決定係数', 'F値', '自由度', 'p値'],
                    '値': [f"{r2:.2f}", f"{f_value:.2f}", f"({df_model}, {df_resid})", f"{p_value:.2f}"]
                })
                # インデックスをリセットして、行番号を非表示に
                summary_df = summary_df.reset_index(drop=True)
                st.dataframe(summary_df)
                
                # 数理モデルの表示
                intercept = model.params[0]
                coefs = model.params[1:]
                equation_terms = [f"{coef:.2f} × {var}" for coef, var in zip(coefs, X_with_const.columns[1:])]
                equation = f"{y_column} = {intercept:.2f} + " + " + ".join(equation_terms)
                st.write("数理モデル：")
                st.write(equation)
                
                # AI解釈機能の追加
                if gemini_api_key and enable_ai_interpretation:
                    st.subheader(f"🤖 AI統計解釈：{y_column}")
                    
                    interpretation_key = f"interpretation_{y_column}"
                    
                    # 解釈ボタン
                    if st.button(f"統計結果を解釈する - {y_column}", key=f"interpret_{y_column}"):
                        with st.spinner("AIが統計結果を分析中..."):
                            # プロンプトを作成
                            prompt = create_statistics_interpretation_prompt(coefficients, summary_df, equation, y_column)
                            
                            # API呼び出し
                            interpretation = call_gemini_api(gemini_api_key, prompt)
                            
                            # 結果をセッション状態に保存
                            st.session_state[interpretation_key] = interpretation
                    
                    # 解釈結果がある場合は常に表示
                    if interpretation_key in st.session_state:
                        st.markdown("### 📊 統計解釈結果")
                        st.write(st.session_state[interpretation_key])
                        
                        # 解釈をクリアするボタン
                        col1, col2 = st.columns([1, 1])
                        with col2:
                            if st.button(f"解釈をクリア", key=f"clear_{y_column}"):
                                del st.session_state[interpretation_key]
                                st.rerun()
                
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
                
                # AI解釈用の結果を保存
                all_analysis_results[y_column] = {
                    'coefficients': coefficients.copy(),
                    'summary': summary_df.copy(),
                    'equation': equation
                }
                
                # パス図の作成
                G = nx.DiGraph()
                
                # ノードの追加（説明変数のみ）
                for var in X_columns:
                    G.add_node(var)
                    all_nodes.add(var)
                G.add_node(y_column)
                all_nodes.add(y_column)
                
                # エッジの追加（有意なもののみ、交互作用項を除く）
                for idx, row in coefficients.iterrows():
                    var = row['変数']
                    coef = float(row['標準化係数']) if row['標準化係数'] != '' else np.nan
                    p_val = float(row['p値']) if row['p値'] != '' else np.nan
                    if var in X_columns:
                        if p_val < 0.1:
                            if abs(coef) >= 0.2:
                                weight = 1  # 太い線
                            elif abs(coef) >= 0.1:
                                weight = 0.5  # 細い線
                            else:
                                continue  # 標準化係数が0.1未満は無視
                            G.add_edge(var, y_column, weight=weight, label=f"{coef:.2f}")
                            all_edges.append({
                                'from': var,
                                'to': y_column,
                                'weight': weight,
                                'coef': f"{coef:.2f}"
                            })
                
                # ノードの位置設定（ユーザーが選択した順番）
                pos = {}
                num_X = len(X_columns)
                y_pos = num_X / 2 + 0.5  # 目的変数の位置
                for idx, var in enumerate(X_columns):
                    pos[var] = (-1, num_X - idx)  # 左側のノード
                pos[y_column] = (1, y_pos)     # 右側のノード
                
                # 図のサイズを計算
                max_var_name_length = max([len(var) for var in X_columns + [y_column]])
                width = max(8, max_var_name_length * 0.5)  # 文字数に応じて横幅を調整
                height = max(6, (len(X_columns) + 2) * 0.6)  # 変数の数に応じて縦幅を調整
                
                # 描画
                fig, ax = plt.subplots(figsize=(width, height))
                
                # ノードラベルの描画
                labels = {node: node for node in G.nodes()}
                
                # ラベルのアライメントを設定
                label_alignment = {}
                for node in G.nodes():
                    if node in X_columns:
                        label_alignment[node] = {'horizontalalignment': 'right', 'pos':(-0.05,0)}
                    elif node in y_columns:
                        label_alignment[node] = {'horizontalalignment': 'left', 'pos':(0.05,0)}
                    else:
                        label_alignment[node] = {'horizontalalignment': 'center', 'pos':(0,0)}
                
                # ノードラベルを個別に描画
                node_bboxes = {}  # ノードのバウンディングボックスを保存
                for node in G.nodes():
                    x, y_pos_node = pos[node]
                    ha = label_alignment[node]['horizontalalignment']
                    offset = label_alignment[node]['pos']
                    text_obj = ax.text(x + offset[0], y_pos_node + offset[1], labels[node], fontsize=10,
                                       bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black"),
                                       horizontalalignment=ha, verticalalignment='center')
                    renderer = fig.canvas.get_renderer()
                    bbox = text_obj.get_window_extent(renderer=renderer)
                    inv = ax.transData.inverted()
                    bbox_data = bbox.transformed(inv)
                    node_bboxes[node] = bbox_data
                
                # エッジの描画
                edges = G.edges()
                weights = [G[u][v]['weight'] * 1.5 for u, v in edges]  # 線の太さを強調
                nx.draw_networkx_edges(G, pos, edgelist=edges, width=weights, arrows=True,
                                       arrowstyle='-|>', arrowsize=20, ax=ax, connectionstyle='arc3,rad=0.0')
                
                # エッジラベルの描画
                edge_labels = nx.get_edge_attributes(G, 'label')
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, ax=ax)
                
                # 統計情報のアノテーション（目的変数のラベルの左端に合わせる）
                x, y_pos_text = pos[y_column]
                # 目的変数のバウンディングボックスから左端の座標を取得
                bbox = node_bboxes[y_column]
                annotation_x = bbox.x0  # 左端のx座標
                ax.text(annotation_x, y_pos_text - 0.5, f"R={np.sqrt(r2):.2f}\nF=({df_model},{df_resid})={f_value:.2f}\n{p_annotation}",
                        horizontalalignment='left', verticalalignment='top', fontsize=10)
                
                # 軸の範囲を調整
                x_margin = 0.6  # 左右の余白を増やす
                ax.set_xlim(-1 - x_margin, 1 + x_margin)
                y_margin = 1  # 上下の余白
                y_min = min(pos[node][1] for node in pos) - y_margin
                y_max = max(pos[node][1] for node in pos) + y_margin
                ax.set_ylim(y_min, y_max)
                
                # 軸の非表示
                plt.axis('off')
                
                st.pyplot(fig)
                plt.close(fig)
            
            # まとめたパス図の作成
            st.subheader("結合されたパス図")
            G_combined = nx.DiGraph()
            
            # ノードの追加
            for node in all_nodes:
                G_combined.add_node(node)
            
            # エッジの追加
            for edge in all_edges:
                G_combined.add_edge(edge['from'], edge['to'], weight=edge['weight'], label=edge['coef'])
            
            # ノードの位置設定（ユーザーが選択した順番）
            pos = {}
            # 説明変数を左側に配置
            num_X = len(X_columns)
            for idx, var in enumerate(X_columns):
                pos[var] = (-1, num_X - idx)
            # 目的変数を右側に配置（R値、F値、判定の表示を考慮して間隔を調整）
            num_Y = len(y_columns)
            spacing = 4  # 目的変数間の縦方向の間隔
            for idx, var in enumerate(y_columns):
                pos[var] = (1, num_Y * spacing - idx * spacing)
            
            # 図のサイズを計算
            max_var_name_length = max([len(var) for var in X_columns + y_columns])
            width = max(8, max_var_name_length * 0.5)  # 文字数に応じて横幅を調整
            height = max(6, (num_X + num_Y * spacing) * 0.6)  # 変数の数に応じて縦幅を調整
            
            # 描画
            fig, ax = plt.subplots(figsize=(width, height))
            
            # ノードラベルの描画
            labels = {node: node for node in G_combined.nodes()}
            
            # ラベルのアライメントを設定
            label_alignment = {}
            for node in G_combined.nodes():
                if node in X_columns:
                    label_alignment[node] = {'horizontalalignment': 'right', 'pos':(-0.05,0)}
                elif node in y_columns:
                    label_alignment[node] = {'horizontalalignment': 'left', 'pos':(0.05,0)}
                else:
                    label_alignment[node] = {'horizontalalignment': 'center', 'pos':(0,0)}
            
            # ノードラベルを個別に描画
            node_bboxes = {}  # ノードのバウンディングボックスを保存
            for node in G_combined.nodes():
                x, y_pos_node = pos[node]
                ha = label_alignment[node]['horizontalalignment']
                offset = label_alignment[node]['pos']
                text_obj = ax.text(x + offset[0], y_pos_node + offset[1], labels[node], fontsize=10,
                                   bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black"),
                                   horizontalalignment=ha, verticalalignment='center')
                renderer = fig.canvas.get_renderer()
                bbox = text_obj.get_window_extent(renderer=renderer)
                inv = ax.transData.inverted()
                bbox_data = bbox.transformed(inv)
                node_bboxes[node] = bbox_data
            
            # エッジの描画
            edges = G_combined.edges()
            weights = [G_combined[u][v]['weight'] * 1.5 for u, v in edges]
            nx.draw_networkx_edges(G_combined, pos, edgelist=edges, width=weights, arrows=True,
                                   arrowstyle='-|>', arrowsize=20, ax=ax, connectionstyle='arc3,rad=0.0')
            
            # エッジラベルの描画
            edge_labels = nx.get_edge_attributes(G_combined, 'label')
            nx.draw_networkx_edge_labels(G_combined, pos, edge_labels=edge_labels, font_size=10, ax=ax)
            
            # 統計情報のアノテーション（目的変数のラベルの左端に合わせる）
            for y_column in y_columns:
                if y_column in pos:
                    x, y_pos_text = pos[y_column]
                    dep_stats = dependent_var_stats[y_column]
                    r2 = dep_stats['r2']
                    f_value = dep_stats['f_value']
                    df_model = dep_stats['df_model']
                    df_resid = dep_stats['df_resid']
                    p_annotation = dep_stats['p_annotation']
                    # 目的変数のバウンディングボックスから左端の座標を取得
                    bbox = node_bboxes[y_column]
                    annotation_x = bbox.x0  # 左端のx座標
                    ax.text(annotation_x, y_pos_text - 1.5, f"R={np.sqrt(r2):.2f}\nF=({df_model},{df_resid})={f_value:.2f}\n{p_annotation}",
                            horizontalalignment='left', verticalalignment='top', fontsize=10)
            
            # 軸の範囲を調整
            x_margin = 0.6  # 左右の余白を増やす
            ax.set_xlim(-1 - x_margin, 1 + x_margin)
            y_margin = 2  # 上下の余白を増やす
            y_min = min(pos[node][1] for node in pos) - y_margin
            y_max = max(pos[node][1] for node in pos) + y_margin
            ax.set_ylim(y_min, y_max)
            
            # 軸の非表示
            plt.axis('off')
            
            st.pyplot(fig)
            plt.close(fig)
            
            # 包括的なAI解釈機能の追加
            if gemini_api_key and enable_ai_interpretation and len(y_columns) > 0:
                st.subheader("🤖 包括的なAI統計解釈")
                st.write("すべての分析結果を統合して、変数間の関係性とシステム全体を解釈します")
                
                comprehensive_key = "comprehensive_interpretation"
                
                # 包括的解釈ボタン
                if st.button("全体的な変数関係を解釈する", key="comprehensive_interpret"):
                    with st.spinner("AIが全体の統計結果を統合分析中..."):
                        # 包括的なプロンプトを作成
                        comprehensive_prompt = create_comprehensive_interpretation_prompt(
                            all_analysis_results, X_columns, y_columns
                        )
                        
                        # API呼び出し
                        comprehensive_interpretation = call_gemini_api(gemini_api_key, comprehensive_prompt)
                        
                        # 結果をセッション状態に保存
                        st.session_state[comprehensive_key] = comprehensive_interpretation
                
                # 包括的解釈結果がある場合は常に表示
                if comprehensive_key in st.session_state:
                    st.markdown("### 📊 包括的統計解釈結果")
                    st.write(st.session_state[comprehensive_key])
                    
                    # 解釈をクリアするボタン
                    col1, col2 = st.columns([1, 1])
                    with col2:
                        if st.button("包括的解釈をクリア", key="clear_comprehensive"):
                            del st.session_state[comprehensive_key]
                            st.rerun()

st.write('')
st.write('')
# フッター
common.display_copyright()
common.display_special_thanks()
