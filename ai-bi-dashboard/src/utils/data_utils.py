import pandas as pd
import numpy as np

def check_dataset_health(df: pd.DataFrame) -> dict:
    """
    Automated checks for the dataset: missing values, duplicate rows, column types, and dataset statistics.
    Returns a dictionary of structured results.
    """
    health_results = {}
    
    # Missing values
    missing_count = df.isnull().sum()
    missing_cols = missing_count[missing_count > 0].to_dict()
    health_results['missing_values'] = missing_cols if missing_cols else "No missing values"
    
    # Duplicate rows
    duplicates = df.duplicated().sum()
    health_results['duplicate_rows'] = int(duplicates)
    
    # Column types
    col_types = df.dtypes.astype(str).to_dict()
    health_results['column_types'] = col_types
    
    # Dataset statistics
    numeric_cols = df.select_dtypes(include=[np.number])
    stats = {}
    if not numeric_cols.empty:
        desc = numeric_cols.describe().to_dict()
        stats = {col: {"mean": vals.get("mean", 0), "min": vals.get("min", 0), "max": vals.get("max", 0)} for col, vals in desc.items()}
    health_results['dataset_statistics'] = stats or "No numeric columns"
    
    # Overall summary logic for llm context
    summary_text = f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns.\n"
    summary_text += f"Total Duplicates: {duplicates}\n"
    if missing_cols:
        summary_text += f"Columns with missing values: {list(missing_cols.keys())}\n"
    if stats:
        summary_text += f"Numeric Columns: {list(stats.keys())}\n"
        
    health_results['summary_text'] = summary_text
    
    return health_results
