import pandas as pd
import streamlit as st
import sqlite3 as sql
from datetime import date, timedelta, datetime
from workoutdata import get_max_microcycle, get_volume_alltime, get_volume_week

st.set_page_config(
    page_icon="🏋🏻",
    layout="wide"
)

last_week = date.today() - timedelta(weeks=1)

st.write("# Volume 💪")

view = st.selectbox(
        "Timeframe",
        ["Overall", "Weekly"])
    
if view != "Overall":
    inputs, chart = st.columns([0.3, 0.7])
    with inputs:
        microcycle_number = st.number_input("Week", min_value=1, max_value = int(get_max_microcycle()))
        dates, data = get_volume_week(microcycle_number)
        latest = dates['Date'].max()
        oldest = dates['Date'].min()
        st.write(f"Showing volume data from {oldest} to {latest}")
    with chart: 
        if microcycle_number:
            st.bar_chart(data, x="Muscle", y="Total Volume", color = "#fcb414")

else: 
    data = get_volume_alltime()
    data['Microcycle'] = data['Microcycle'].astype(int)
    st.line_chart(data=data, x="Microcycle", y="Total Volume", color = "Muscle", x_label="Week", y_label="Number of Sets")