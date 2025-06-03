import matplotlib.pyplot as plt

import streamlit as st
import japanize_matplotlib


def display_header():
    st.caption('Created by Dit-Lab.(Daiki Ito)')


def set_font():
    font_path = '../ipaexg.ttf'  # pages フォルダから一つ上を見る
    plt.rcParams['font.family'] = 'IPAexGothic'


def display_guide():
    st.markdown("""
    - [**情報探究ステップアップガイド**](https://dit-lab.notion.site/612d9665350544aa97a2a8514a03c77c?v=85ad37a3275b4717a0033516b9cfd9cc)
    - [**中の人のページ（Dit-Lab.）**](https://dit-lab.notion.site/Dit-Lab-da906d09d3cf42a19a011cf4bf25a673?pvs=4)
    """)


def display_link():
    st.header('リンク')
    st.markdown("""
    - [**中の人のページ（Dit-Lab.）**](https://dit-lab.notion.site/Dit-Lab-da906d09d3cf42a19a011cf4bf25a673?pvs=4)
    - [**進数変換学習アプリ**](https://easy-base-converter.streamlit.app)
    - [**easyRSA**](https://easy-rsa.streamlit.app/)
    - [**easyAutoML（回帰）**](https://huggingface.co/spaces/itou-daiki/pycaret_datascience_streamlit)
    - [**pkl_predict_reg**](https://huggingface.co/spaces/itou-daiki/pkl_predict_reg)
    - [**音のデータサイエンス**](https://audiovisualizationanalysis-bpeekdjwymuf6nkqcb4cqy.streamlit.app)
    - [**3D RGB Cube Visualizer**](https://boxplot-4-mysteams.streamlit.app)
    - [**上マーク角度計算補助ツール**](https://sailing-mark-angle.streamlit.app)
    - [**Factor Score Calculator**](https://factor-score-calculator.streamlit.app/)
    - [**easy Excel Merge**](https://easy-xl-merge.streamlit.app)
    - [**フィードバックはこちらまで**](https://forms.gle/G5sMYm7dNpz2FQtU9)
    - [**ソースコードはこちら（GitHub）**](https://github.com/itou-daiki/easy_stat)
    """)


def display_copyright():
    st.subheader('')
    st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
    st.write('')
    st.subheader('© 2022-2025 Dit-Lab.(Daiki Ito). All Rights Reserved.')
    st.write('easyStat: Open Source for Ubiquitous Statistics')
    st.write('Democratizing data, everywhere.')
    st.write('')


def display_special_thanks():
    st.subheader('In collaboration with our esteemed contributors:')
    st.write('・Toshiyuki')
    st.write('With heartfelt appreciation for their dedication and support.')
