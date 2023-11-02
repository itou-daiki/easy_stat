# 必要なライブラリをインポート
import streamlit as st
import pandas as pd
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
import plotly.offline as py

# タイトルを設定
st.title('因子分析アプリ')
st.caption("Created by Dit-Lab.(Daiki Ito)")

# CSVまたはExcelファイルのアップロード
uploaded_file = st.file_uploader("CSVまたはExcelファイルをアップロードしてください", type=["csv", "xlsx"])
if uploaded_file is not None:
    # ファイルの拡張子に応じて読み込み
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        data = pd.read_excel(uploaded_file)
    
    st.write(data)

    # データが2つのカラム（dsとy）を持っていることを確認
    if 'ds' not in data.columns or 'y' not in data.columns:
        st.write("ファイルは 'ds' と 'y' の2つのカラムを持つ必要があります。")
    else:
        # Prophetモデルの設定と学習
        model = Prophet()
        model.fit(data)

        # 未来の日付を予測するためのデータフレームを作成
        future = model.make_future_dataframe(periods=365)
        forecast = model.predict(future)

        # 予測結果の表示
        st.write('予測結果:')
        st.write(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])

        # 予測のグラフを表示
        fig1 = model.plot(forecast)
        st.write(fig1)

        # トレンドや週次、年次の影響を表示
        fig2 = model.plot_components(forecast)
        st.write(fig2)

st.markdown('© 2022-2023 Dit-Lab.(Daiki Ito). All Rights Reserved.')

