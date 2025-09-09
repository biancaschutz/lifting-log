import pandas as pd
import streamlit as st
import sqlite3 as sql

st.write("# 1RM Trends 🏆")

# Load data
with sql.connect("workout_log.db") as conn:
    exercises = pd.read_sql_query("SELECT Exercise from log", conn).sort_values(by='Exercise')['Exercise'].unique().tolist()

exercise = st.selectbox('View Exercise', exercises)

with sql.connect("workout_log.db") as conn:
    query = "SELECT v.Date, MAX(v.Volume) as Best, v.Reps, v.Load FROM (SELECT Date, Exercise, Reps, Load, Reps * Load as Volume FROM log WHERE Exercise = ?) v GROUP BY v.Date"
    record = pd.read_sql_query(query, conn, params=(exercise,))

record['ONERM'] = record['Load'] / (1.0278 - 0.0278 * record['Reps'])

record["Date"] = pd.to_datetime(record["Date"], errors='coerce')

record["DateNew"] = record["Date"].dt.strftime('%-m/%-d')

st.line_chart(data=record, x="DateNew", y="ONERM", x_label="Date", y_label="Weight (lbs)")