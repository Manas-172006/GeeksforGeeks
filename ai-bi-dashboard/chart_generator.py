import matplotlib.pyplot as plt
import pandas as pd

class ChartGenerator:
    def __init__(self):
        plt.style.use('default')
        
    def generate_chart(self, analysis_result: dict, intent: str):
        """
        Takes the analysis result dictionary and generates a basic chart.
        If the intent implies a chart or chart naturally fits the data, it returns a figure.
        """
        # Close any existing figures to avoid overlap
        plt.close('all')
        
        if 'error' in analysis_result:
            return None
            
        data = analysis_result.get('data')
        if data is None or data.empty:
            return None
            
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # If the result itself is plotting-ready (like sum or average)
        if intent in ['sum', 'average', 'max', 'min']:
            # We plotted numeric series, 'data' is a dataframe. Let's plot the results.
            res = analysis_result.get('result')
            if isinstance(res, dict):
                series = pd.Series(res)
                series.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
                ax.set_title(f"{intent.capitalize()} values across columns")
                ax.set_ylabel("Value")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                return fig
                
        # For general charts, let's look at the structure of 'data'
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            if len(data.columns) == 2 and len(numeric_cols) == 1:
                # E.g., Date and Sales
                cat_col = [c for c in data.columns if c not in numeric_cols][0]
                num_col = numeric_cols[0]
                data.plot(x=cat_col, y=num_col, kind='bar', ax=ax, title=f"{num_col} by {cat_col}", legend=False)
                plt.xticks(rotation=45, ha='right')
            else:
                # E.g., multiple numeric cols - plot the first one as histogram
                num_col = numeric_cols[0]
                data[num_col].hist(ax=ax, bins=15, color='lightgreen', edgecolor='black')
                ax.set_title(f"Distribution of {num_col}")
                ax.set_xlabel(num_col)
                ax.set_ylabel("Frequency")
        else:
            # Categorical only distribution
            if len(data.columns) > 0:
                col = data.columns[0]
                data[col].value_counts().head(10).plot(kind='pie', autopct='%1.1f%%', ax=ax)
                ax.set_title(f"Distribution of {col}")
                ax.set_ylabel("")
        
        plt.tight_layout()
        return fig
