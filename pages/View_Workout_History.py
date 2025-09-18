## view log

import streamlit as st
import sqlite3 as sql
import pandas as pd

with sql.connect("workout_log.db") as conn:
        query = """
        SELECT *
        FROM log
        """
        log = pd.read_sql_query(query, conn)

st.write("Here, you can manually add, edit, or remove any sets.")

updated_log = st.data_editor(log, num_rows= "dynamic")

with sql.connect("workout_log.db") as conn:
      updated_log.to_sql("log", conn, if_exists='replace', chunksize=1000, index=False)