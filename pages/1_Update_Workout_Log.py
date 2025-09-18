import pandas as pd
import streamlit as st
import sqlite3 as sql

st.set_page_config(
    page_icon="🏋🏻")

def get_new_microcycle():
    with sql.connect("workout_log.db") as conn:
        query = """
        SELECT MAX(Microcycle) AS max_micro
        FROM log
        """
        last_micro = pd.read_sql_query(query, conn)['max_micro'][0]
        query2 = """
        SELECT Routine
        FROM log
        ORDER BY Date DESC
        LIMIT 1;
        """
        last_routine = pd.read_sql_query(query2, conn)['Routine'][0]
        microcycle = last_micro
        if last_routine == "5. BT":
            microcycle += 1
        return microcycle

st.write("# Update workout log 📝")

# text for upload interface
st.write("## Upload a workout CSV file here")

st.write("The file must contain the columns Date, Routine, Exercise, Reps, and Load. Download a template on the How-To page.")

# upload button
uploaded_file = st.file_uploader("Choose a file", type="csv")

# load uploaded csv into pandas dataframe
with st.form("workout_upload"):
    if uploaded_file is not None:
        new_workout = pd.read_csv(uploaded_file)
        st.write(new_workout)
        new_workout['Microcycle'] = get_new_microcycle()
        submitted_workout = st.form_submit_button('Add Workout')
        if submitted_workout:
            try:
                with sql.connect("workout_log.db") as conn:
                    new_workout.to_sql("log", conn, if_exists='append', chunksize=1000, index=False)
                st.success(f"Successfully added this workout to the log.")
            except Exception as e:
                st.error(f"Failed to insert data into log: {e}")