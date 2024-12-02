import pandas as pd

def load_data():
    try:
        data_levels = pd.read_csv('Data_Levels.csv')
        data_dailys = pd.read_csv('Data_Dailys.csv')

        if data_levels.empty or data_dailys.empty:
            raise ValueError("Data files are empty or not properly formatted.")

        return data_levels, data_dailys

    except Exception as e:
        raise ValueError(f"Error loading data: {e}")
