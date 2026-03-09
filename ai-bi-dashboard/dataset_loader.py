# Dataset Loader
# Loads and preprocesses datasets for the BI dashboard

import pandas as pd

class DatasetLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_dataset(self):
        # Load the dataset from file
        # TODO: Add error handling and data validation
        try:
            df = pd.read_csv(self.file_path)
            return df
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            return None