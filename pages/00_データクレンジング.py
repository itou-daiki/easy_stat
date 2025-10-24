import io

import streamlit as st
import numpy as np
import pandas as pd

import common


st.set_page_config(page_title='データクレンジング', layout='wide')

st.title('データクレンジング')
common.display_header()
st.write('データセットに対して、欠損値処理や外れ値の処理などができます')
st.write('')

# ファイルアップローダー
uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])

if uploaded_file is not None:
    # データの読み込み
    if uploaded_file.type == 'text/csv':
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)
    
    st.subheader('元のデータ')
    st.write(data)

    processed_data = data

    # 処理オプション
    remove_outliers_option = st.checkbox('外れ値の削除')
    data_cleansing_option = st.checkbox('欠損値の削除')
    remove_empty_columns_option = st.checkbox('値が入っていないカラム（列）の削除')

    if st.button('データ処理'):
        # 外れ値の削除
        if remove_outliers_option:
            num_cols = processed_data.select_dtypes(include=np.number).columns
            if not num_cols.empty:
                Q1 = processed_data[num_cols].quantile(0.25)
                Q3 = processed_data[num_cols].quantile(0.75)
                IQR = Q3 - Q1
                outlier_condition = (
                    (processed_data[num_cols] < (Q1 - 1.5 * IQR)) | 
                    (processed_data[num_cols] > (Q3 + 1.5 * IQR))
                )
                processed_data = processed_data[~outlier_condition.any(axis=1)]
            else:
                st.warning('外れ値を削除する数値列がありません')

        # 欠損値の削除
        if data_cleansing_option:
            processed_data = processed_data.dropna()
            processed_data = processed_data.applymap(
                lambda x: x.strip() if isinstance(x, str) else x
            )

        # 空のカラムの削除
        if remove_empty_columns_option:
            empty_columns = processed_data.columns[data.isna().all()].tolist()
            processed_data = processed_data.dropna(axis=1, how='all')

        st.subheader('処理済みのデータ')
        st.write(processed_data)

        # ファイル形式の選択
        file_format = st.selectbox('ダウンロードするファイル形式を選択', ['Excel', 'CSV'])

        # ファイル名の作成
        download_file_name = f"{uploaded_file.name.rsplit('.', 1)[0]}_processed"
        
        # ダウンロードボタン
        if file_format == 'CSV':
            csv_data = processed_data.to_csv(index=False)
            st.download_button(
                label='処理済みデータをダウンロード',
                data=csv_data,
                file_name=f'{download_file_name}.csv',
                mime='text/csv'
            )
        else:
            excel_io = io.BytesIO()
            processed_data.to_excel(excel_io, index=False)
            excel_data = excel_io.getvalue()
            st.download_button(
                label='処理済みデータをダウンロード',
                data=excel_data,
                file_name=f'{download_file_name}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

# フッター
common.display_copyright()
common.display_special_thanks()
