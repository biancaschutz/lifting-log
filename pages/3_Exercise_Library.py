import pandas as pd
import streamlit as st
import sqlite3 as sql

st.set_page_config(layout="wide",
    page_icon="🏋🏻"
)

def load_data():
    with sql.connect("workout_log.db") as conn:
        routines = pd.read_sql_query("SELECT * from exercises", conn)
    return routines.rename(columns={'Primary': 'Primary Muscle', 'Secondary': 'Secondary Muscles'})

routines_cleaned = load_data()

if "success_msg" in st.session_state:
    st.success(st.session_state["success_msg"])
    del st.session_state["success_msg"] 

st.write("# Exercise Library 🏋🏻")

view_exercises, add_exercise = st.columns([0.5, 0.5])

with view_exercises:
    st.dataframe(data=routines_cleaned,width="stretch")

with add_exercise:
    st.header("Add a new exercise")

    with st.form("set_upload"):

        name = st.text_input("Exercise Name", placeholder = "Include equipment if applicable")

        primary = st.selectbox(
        "Primary Muscle Worked",
        ["Abs", "Biceps", "Calves", "Chest", "Glutes", "Hamstrings", "Lats", "Quads", "Shoulders", "Traps", "Triceps", "Upper Back"],
        index=None,
        accept_new_options=True,
    )

        secondary = st.multiselect(
            "Secondary Muscles Worked",
            ["Abs", "Biceps", "Calves", "Chest", "Glutes", "Hamstrings", "Lats", "Quads", "Shoulders", "Traps", "Triceps", "Upper Back"],
            accept_new_options=True
        )

        secondaries = ", ".join(secondary)

        print(secondaries)
        submitted = st.form_submit_button('Add Exercise')
        if submitted:
            try:
                with sql.connect("workout_log.db") as conn:
                    cursor = conn.cursor()
                    insert_query = """
                        INSERT INTO exercises (Exercise, "Primary", Secondary)
                        VALUES (?, ?, ?)
                    """
                    cursor.execute(insert_query, (name, primary, secondaries))
                    conn.commit()
                st.session_state["success_msg"] = f"Successfully added {name} to the exercise library."
                # rerun to add it to the library and reload table so user can see it was successfully added
                st.rerun()


            except Exception as e:
                st.error(f"Failed to insert data into exercise library: {e}")