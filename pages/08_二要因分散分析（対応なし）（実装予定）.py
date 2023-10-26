import math

import streamlit as st
import pandas as pd
# 実装予定
# import matplotlib.pyplot as plt
from scipy import stats
from PIL import Image

import matplotlib as mpl
# フォントのプロパティを設定
font_prop = mpl.font_manager.FontProperties(fname="ipaexg.ttf")
# Matplotlibのデフォルトのフォントを変更
mpl.rcParams['font.family'] = font_prop.get_name()

st.set_page_config(page_title="二要因分散分析（対応なし）", layout="wide")

st.title("二要因分散分析（対応なし）")
st.caption("Created by Daiki Ito")
st.write("")
st.subheader("ブラウザで検定　→　表　→　解釈まで出力できるウェブアプリです。")
st.write("iPad等でも分析を行うことができます")

st.write("")

st.write("実装予定")
