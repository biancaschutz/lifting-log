import pandas as pd
import streamlit as st
import sqlite3 as sql
from workoutdata import calculate_1RM

st.set_page_config(
    page_icon="🏋🏻"
)

st.write("# 1RM Trends 🏆")

# Load data
with sql.connect("workout_log.db") as conn:
    exercises = pd.read_sql_query("SELECT Exercise from log", conn).sort_values(by='Exercise')['Exercise'].unique().tolist()

exercise = st.selectbox('View Exercise', exercises)

with sql.connect("workout_log.db") as conn:
    query = "SELECT v.Date, MAX(v.Volume) as Best, v.Reps, v.Load FROM (SELECT Date, Exercise, Reps, Load, Reps * Load as Volume FROM log WHERE Exercise = ?) v GROUP BY v.Date"
    record = pd.read_sql_query(query, conn, params=(exercise,))

record['One Rep Max'] = calculate_1RM(record['Load'], record['Reps'])

record["Date"] = pd.to_datetime(record["Date"], errors='coerce')

fmt = "%m-%d"

st.line_chart(data=record, x="Date", y="One Rep Max", x_label="Date", y_label="Weight (lbs)")