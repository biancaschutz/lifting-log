import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏋🏻",
)

st.write("# Weightlifting Tracker 🏋🏻")

st.markdown(
        """
        First draft. Currently able to calculate 1RM and add entries to DB file.
        App is meant to run locally using SQLite as data storage.

        Functionalities coming:
        Volume per week
        Home page becomes dashboard-like
        Able to change and view routines (calendar maybe?)
        """)