###
# DATA MANIPULATION FUNCTIONS
### 

# IMPORTS
import pandas as pd
import sqlite3 as sql
from datetime import date, timedelta, datetime

def get_max_microcycle():
    """
    Helper function that returns the last/ongoing microcycle (workout week) in the log table.

    Inputs: none

    Outputs: 
        - an integer representing the microcycle/workout week number
    """
    # connecting to the db
    with sql.connect("workout_log.db") as conn:
        # we need the maximum Microcycle
        query = """
        SELECT MAX(Microcycle) AS max_micro
        FROM log
        """
        # getting the first value of the Microcycle column
        last_micro = pd.read_sql_query(query, conn)['max_micro'][0]

        return last_micro
    
def get_workout_routine(input_date):
    """
    Helper function that grabs the workout routine performed in a session on a particular date.

    Inputs: 
        - input_date, a string
    
    Outputs:
        - a string listing the workout routine performed that day, or if
        it was a rest day or the day is yet to occur
    """
    # accounting for the case in which the date is in the future
    if datetime.strptime(input_date, "%m/%d/%Y") > datetime.today():
        return "TBD"
    # connecting to the workout db
    with sql.connect("workout_log.db") as conn:
        # getting the routine from the date
        routine_date = pd.read_sql_query(
            "SELECT DISTINCT Routine FROM log WHERE Date = ?",
            conn,
            params=(input_date,) 
        )
        # if there was a workout found, return the routine
        if not routine_date.empty:
            return routine_date['Routine'][0]
        # otherwise, it was a rest day
        else:
            return "Rest Day"
        
def get_volume_alltime():
    """
    Helper function that calculates the volume per muscle group per microcycle (workout week), returns a DataFrame.

    Note that sets performed for secondary muscle groups are counted as 0.5 sets for that particular muscle group. 

    Inputs:
        - none
    
    Outputs: 
        - pandas DataFrame with columns Microcycle (the week), Muscle (the muscle group), 
        and Total Volume (volume per week and muscle group)
    """
    with sql.connect("workout_log.db") as conn:
        # getting the necessary information
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

        # getting the sets per muscle group and microcycle
        primary_sets = alltime_exercises.value_counts(["Microcycle", "Primary"])

        # the secondary muscle groups are stored as a string, so separating that out into columns
        alltime_exercises['Secondary_split'] = alltime_exercises['Secondary'].str.split(", ")
        exploded = alltime_exercises.explode('Secondary_split')

        exploded = exploded.dropna(subset=['Secondary_split'])

        secondary_sets = exploded.value_counts(["Microcycle", "Secondary_split"]).reset_index(name='count')

        # calculating the sets accounting for secondary muscle group (not the primary focus so not a full set)
        secondary_sets['Secondary'] = secondary_sets['count'] * 0.5

        # selecting the columns we need and renaming
        secondary = secondary_sets[['Microcycle', 'Secondary_split', 'Secondary']].rename(columns={'Secondary_split': 'Muscle'})

        # renaming and preparing primary muscle data for the merge
        primary_sets2 = primary_sets.reset_index(name='count')  

        primary = primary_sets2.rename(columns={'Primary': 'Muscle'})
        
        # combining the two dataframes based on week and muscle and filling NAs as 0 to ensure correct calculations in next step
        merged_sets = pd.merge(primary, secondary, on = ['Microcycle', 'Muscle'], how='outer').fillna(0)

        # combining secondary and primary sets per muscle per week to get volume
        merged_sets["Total Volume"] = merged_sets["count"] + merged_sets["Secondary"]

        return merged_sets[['Microcycle', 'Muscle', 'Total Volume']]
    

def get_volume_week(microcycle):
    """
    Helper function that calculates the volume per muscle group for a particular microcycle/workout week, returns a DataFrame.

    Note that sets performed for secondary muscle groups are counted as 0.5 sets for that particular muscle group. 

    Inputs:
        - none
    
    Outputs: a tuple containing the below
        - tuple index 0: a pandas DataFrame with a singular column containing the dates worked out from that microcycle
        - tuple index 1: pandas DataFrame with columns Muscle (the muscle group) and Total Volume (volume per muscle group)
    """
    with sql.connect("workout_log.db") as conn:
        query = """
        SELECT l.Date, l.Exercise, e."Primary", e.Secondary
        FROM (SELECT * FROM log WHERE Microcycle = ?) l
        LEFT JOIN exercises e
        ON l.Exercise = e.Exercise
        """
        exercises_range = pd.read_sql_query(
            query,
            conn,
            params=(microcycle,) 
        )

        # getting the dates for this microcycle
        dates = exercises_range[['Date']]

        # same steps as above, just not grouping by microcycle
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

        return dates, merged_sets[['Muscle', 'Total Volume']]
    
def calculate_1RM(load, reps):
    """
    Helper function that calculates the 1 rep maximum for an exercise using the Brzycki formula.

    Inputs:
        - value or DataFrame column containing load for a set
        - value or DataFrame column containing the number of reps for a set

    Outputs: 
        - value or DataFrame column, depending on inputs, with the 1RM calculation
    """
    return round(load / (1.0278 - 0.0278 * reps), 2)