import pandas as pd
import streamlit as st
import sqlite3 as sql

# Load data
with sql.connect("workout_log.db") as conn:
    routines = pd.read_sql_query("SELECT * from routines", conn)

st.write("# Log a new set 📝")

date = st.date_input(label = "Date", format="MM/DD/YYYY").strftime('%-m/%-d/%Y')

routine_dropdown = routines['Routine'].unique().tolist()
routine = st.selectbox('Select Routine', routine_dropdown)

# Filter exercises based on selected routine
filtered_exercises = routines[routines['Routine'] == routine]['Exercise'].tolist()

# Now create form for the rest
with st.form("my_form"):
    selected_exercise = st.selectbox("Select Exercise", filtered_exercises)
    reps = st.number_input(key='reps', label='Number of Reps', min_value=0)
    
    load = st.number_input(key='load', label='Load', min_value=0)

    submitted = st.form_submit_button('Add Set')
    if submitted:
        try:
            with sql.connect("workout_log.db") as conn:
                cursor = conn.cursor()
                insert_query = """
                    INSERT INTO log (Date, Routine, Exercise, Reps, Load)
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(insert_query, (date, routine, selected_exercise, reps, load))
                conn.commit()
            st.success(f"Successfully added {reps} reps for {selected_exercise} on {date} to the log.")
        except Exception as e:
            st.error(f"Failed to insert data into log: {e}")