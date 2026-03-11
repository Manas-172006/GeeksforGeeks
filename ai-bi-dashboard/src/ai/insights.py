import pandas as pd
import numpy as np

def generate_insights(df: pd.DataFrame) -> list:
    """
    Automatically analyze dataset and generate simple insights.
    """
    insights = []
    
    # 1. Dataset statistics
    insights.append(f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns.")
    
    # Identify column types
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()

    # 2. Columns with missing values
    missing_counts = df.isnull().sum()
    missing_cols = missing_counts[missing_counts > 0]
    if not missing_cols.empty:
        for col, count in missing_cols.items():
            insights.append(f"Column '{col}' contains {count} missing values.")
    else:
        insights.append("No missing values found in the dataset.")

    # 3. Strongest correlation between numeric variables
    if len(numeric_cols) > 1:
        try:
            corr_matrix = df[numeric_cols].corr()
            upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
            max_corr = upper.unstack().dropna().sort_values(ascending=False).head(1)
            if not max_corr.empty:
                col1, col2 = max_corr.index[0]
                val = max_corr.values[0]
                if abs(val) > 0.5:
                    insights.append(f"'{col1}' strongly correlates with '{col2}' ({val:.2f}).")
        except Exception:
            pass

    # 4. Column with highest variance
    if numeric_cols:
        try:
            variances = df[numeric_cols].var().dropna()
            if not variances.empty:
                highest_var_col = variances.idxmax()
                insights.append(f"Column '{highest_var_col}' has the highest variance among numeric features.")
        except Exception:
            pass

    # 5. Most frequent category in categorical columns
    if categorical_cols:
        try:
            for col in categorical_cols[:3]: # Limit to top 3 to avoid clutter
                freq = df[col].value_counts()
                if not freq.empty:
                    top_cat = freq.index[0]
                    insights.append(f"In column '{col}', '{top_cat}' has the highest frequency.")
        except Exception:
            pass

    return insights

def recommend_charts(df: pd.DataFrame) -> list:
    """
    Automatically suggest useful visualizations based on dataset structure.
    """
    recommendations = []
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    
    if len(numeric_cols) >= 2:
        recommendations.append(f"Scatter plot between {numeric_cols[0]} and {numeric_cols[1]}")
    
    if len(categorical_cols) >= 1:
        recommendations.append(f"Bar chart of {categorical_cols[0]} distribution")
        
    if len(numeric_cols) >= 1:
        recommendations.append(f"Histogram of {numeric_cols[0]}")
        if len(categorical_cols) >= 1:
            recommendations.append(f"Box plot of {numeric_cols[0]} by {categorical_cols[0]}")

    return recommendations
