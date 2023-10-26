import streamlit as st
import numpy as np
import pandas as pd
import io






st.set_page_config(page_title="データクレンジング", layout="wide")

st.title("データクレンジング")
st.caption("Created by Daiki Ito")
st.write("データセットに対して、欠損値処理や外れ値の処理などができます")
st.write("")

uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.type == 'text/csv':
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)
    
    st.subheader('元のデータ')
    st.write(data)

    remove_outliers_option = st.checkbox('外れ値の削除')
    data_cleansing_option = st.checkbox('欠損値の削除')
    remove_empty_columns_option = st.checkbox('値が入っていないカラム（列）の削除')

    if st.button('データ処理'):
        process_history = {}  # 処理の履歴を格納する辞書

        if remove_outliers_option:
            num_cols = data.select_dtypes(include=np.number).columns
            if not num_cols.empty:
                Q1 = data[num_cols].quantile(0.25)
                Q3 = data[num_cols].quantile(0.75)
                IQR = Q3 - Q1
                outlier_condition = ((data[num_cols] < (Q1 - 1.5 * IQR)) | (data[num_cols] > (Q3 + 1.5 * IQR)))
                data = data[~outlier_condition.any(axis=1)]
                process_history['【外れ値の削除】'] = '＜外れ値を削除したカラム（列）＞:\n{}'.format(",\n　".join(num_cols))
            else:
                st.warning('外れ値を削除する数値列がありません')

        if data_cleansing_option:
            data = data.dropna()
            data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            process_history['【欠損値の削除】'] = '欠損値の削除と文字列の空白の削除を行いました'

        if remove_empty_columns_option:
            empty_columns = data.columns[data.isna().all()].tolist()
            data = data.dropna(axis=1, how='all')
            process_history['【値が入っていないカラム（列）の削除】'] = '＜削除されたカラム＞:\n{}'.format(",\n　".join(empty_columns))

        st.subheader('処理済みのデータ')
        st.write(data)

        st.subheader('処理の履歴')
        for process, details in process_history.items():
            st.text(f'{process}:\n{details}') 

        file_format = st.selectbox('ダウンロードするファイル形式を選択', ['Excel', 'CSV'])
        if file_format == 'CSV':
            csv_data = data.to_csv(index=False)
            st.download_button(
                label="処理済みデータをダウンロード",
                data=csv_data,
                file_name=f'processed_data.csv',
                mime='text/csv'
            )
        else:
            excel_io = io.BytesIO()  # BytesIOオブジェクトを作成
            data.to_excel(excel_io, index=False)  # ExcelデータをBytesIOオブジェクトに書き込む
            excel_data = excel_io.getvalue()  # BytesIOオブジェクトからバイトデータを取得
            st.download_button(
                label="処理済みデータをダウンロード",
                data=excel_data,
                file_name=f'processed_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    
st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
