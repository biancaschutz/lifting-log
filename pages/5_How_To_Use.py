import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_icon="🏋🏻")

st.write("# How to use this app")

st.write("## Download a template workout csv")

@st.cache_data
def get_data():
    df = pd.read_csv("template.csv")
    return df

@st.cache_data
def convert_for_download(df):
    return df.to_csv(index=False).encode("utf-8")

df = get_data()
csv = convert_for_download(df)

st.download_button("Download CSV Template", csv, file_name=f"template_{date.today().month}_{date.today().day}.csv")