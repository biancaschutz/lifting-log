import pandas as pd
import streamlit as st
import sqlite3 as sql
from datetime import date, timedelta, datetime


st.set_page_config(
    page_icon="🏋🏻",
    layout="wide"
)

def get_workout_routine(input_date):
    if datetime.strptime(input_date, "%m/%d/%Y") > datetime.today():
        return "TBD"
    with sql.connect("workout_log.db") as conn:
        routine_date = pd.read_sql_query(
            "SELECT DISTINCT Routine FROM log WHERE Date = ?",
            conn,
            params=(input_date,) 
        )
        if not routine_date.empty:
            return routine_date['Routine'][0]
        else:
            return "Rest Day"
        
def get_volume_alltime():
    with sql.connect("workout_log.db") as conn:
        query = """
        SELECT l.Date, l.Exercise, e."Primary", e.Secondary, l.Microcycle
        FROM log l
        LEFT JOIN exercises e
        ON l.Exercise = e.Exercise
        """
        alltime_exercises = pd.read_sql_query(
            query,
            conn
        )

        primary_sets = alltime_exercises.value_counts(["Microcycle", "Primary"])

        alltime_exercises['Secondary_split'] = alltime_exercises['Secondary'].str.split(", ")
        exploded = alltime_exercises.explode('Secondary_split')

        exploded = exploded.dropna(subset=['Secondary_split'])

        secondary_sets = exploded.value_counts(["Microcycle", "Secondary_split"]).reset_index(name='count')

        secondary_sets['Secondary'] = secondary_sets['count'] * 0.5

        secondary = secondary_sets[['Microcycle', 'Secondary_split', 'Secondary']].rename(columns={'Secondary_split': 'Muscle'})

        primary_sets2 = primary_sets.reset_index(name='count')  

        primary = primary_sets2.rename(columns={'Primary': 'Muscle'})
        
        merged_sets = pd.merge(primary, secondary, on = ['Microcycle', 'Muscle'], how='outer').fillna(0)

        merged_sets["Total Volume"] = merged_sets["count"] + merged_sets["Secondary"]

        return merged_sets[['Microcycle', 'Muscle', 'Total Volume']]
    

def get_volume_week(start, end):
    with sql.connect("workout_log.db") as conn:
        query = """
        SELECT l.Date, l.Exercise, e."Primary", e.Secondary
        FROM (SELECT * FROM log WHERE Date >= ? AND Date <= ?) l
        LEFT JOIN exercises e
        ON l.Exercise = e.Exercise
        """
        exercises_range = pd.read_sql_query(
            query,
            conn,
            params=(start, end) 
        )

        primary_sets = exercises_range.value_counts(["Primary"])

        exercises_range['Secondary_split'] = exercises_range['Secondary'].str.split(", ")
        exploded = exercises_range.explode('Secondary_split')

        exploded = exploded.dropna(subset=['Secondary_split'])

        secondary_sets = exploded.value_counts(["Secondary_split"]).reset_index(name='count')

        secondary_sets['Secondary'] = secondary_sets['count'] * 0.5

        secondary = secondary_sets[['Secondary_split', 'Secondary']].rename(columns={'Secondary_split': 'Muscle'})

        primary_sets2 = primary_sets.reset_index(name='count')  

        primary = primary_sets2.rename(columns={'Primary': 'Muscle'})
        
        merged_sets = pd.merge(primary, secondary, on = ['Muscle'], how='outer').fillna(0)

        merged_sets["Total Volume"] = merged_sets["count"] + merged_sets["Secondary"]

        return merged_sets[['Muscle', 'Total Volume']]

last_week = date.today() - timedelta(weeks=1)

st.write("# Volume 💪")

view = st.selectbox(
        "Timeframe",
        ["Overall", "Weekly"])
    
if view != "Overall":
    inputs, chart = st.columns([0.3, 0.7])
    with inputs:
        start_date = st.date_input("Start", value=last_week, format="MM/DD/YYYY")

        if start_date:
            routine = get_workout_routine(start_date.strftime("%-m/%-d/%Y"))  
            st.write(f"Routine on {start_date.strftime("%-m/%-d/%Y")}: {routine}")

        end_date = st.date_input("End", value=date.today(), format="MM/DD/YYYY", min_value=start_date + timedelta(days=1))

        if end_date:
            routine = get_workout_routine(end_date.strftime("%-m/%-d/%Y"))  
            st.write(f"Routine on {end_date.strftime("%-m/%-d/%Y")}: {routine}")
    with chart: 
        if start_date and end_date:
            data = get_volume_week(start_date.strftime("%-m/%-d/%Y"), end_date.strftime("%-m/%-d/%Y"))
            st.bar_chart(data, x="Muscle", y="Total Volume", color = "#fcb414")

else: 
    data = get_volume_alltime()
    st.line_chart(data=data, x="Microcycle", y="Total Volume", color = "Muscle", x_label="Week", y_label="Number of Sets")
        