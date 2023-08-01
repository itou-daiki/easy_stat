import math
import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline
from scipy import stats
from PIL import Image

import matplotlib as mpl
# フォントのプロパティを設定
font_prop = mpl.font_manager.FontProperties(fname="ipaexg.ttf")
# Matplotlibのデフォルトのフォントを変更
mpl.rcParams['font.family'] = font_prop.get_name()

st.set_page_config(page_title="主成分分析", layout="wide")

st.title("主成分分析")
st.caption("Created by Daiki Ito")
st.write("")
st.subheader("ブラウザで検定　→　表　→　解釈まで出力できるウェブアプリです。")
st.write("iPad等でも分析を行うことができます")

st.write("")

st.write("実装予定")


def load_data(file):
    df = pd.read_excel(file)
    return df


def preprocess(df):
    # Identify categorical variables
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns

    # Apply one-hot encoding to categorical variables
    preprocessor = make_column_transformer(
        (OneHotEncoder(), categorical_cols),
        (StandardScaler(), numerical_cols),
        remainder='passthrough'
    )

    df_preprocessed = preprocessor.fit_transform(df)
    return df_preprocessed


def run_pca(df, n_components):
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df)

    pca = PCA(n_components=n_components)
    components = pca.fit_transform(df_scaled)

    return components, pca


uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx'])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.write(df)

    df_preprocessed = preprocess(df)
    st.write("Preprocessed data:")
    st.write(df_preprocessed)

    n_components = st.slider("Number of components", 1, min(df_preprocessed.shape[1], 8))
    components, pca = run_pca(df_preprocessed, n_components)

    st.write("Explained variance ratio:")
    st.write(pca.explained_variance_ratio_)

    st.write("Principal components:")
    st.write(components)