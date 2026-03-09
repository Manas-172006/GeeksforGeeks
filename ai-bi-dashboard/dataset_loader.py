# Dataset Loader
# Loads and preprocesses datasets for the BI dashboard

import pandas as pd

def load_dataset():
    try:
        df = pd.read_csv("data/Nykaa Digital Marketing.csv", encoding='latin1')
        df.columns = df.columns.str.strip()
        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame()

if __name__ == "__main__":
    df = load_dataset()
    print(df.head())