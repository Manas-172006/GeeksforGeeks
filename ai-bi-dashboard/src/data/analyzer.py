import pandas as pd

class DataAnalyzer:
    def __init__(self):
        pass
        
    def analyze(self, df: pd.DataFrame, parsed_query: dict) -> dict:
        """
        Executes basic Pandas operations based on the parsed intent and columns.
        Returns a dictionary containing the result or relevant subset of the DataFrame.
        """
        intent = parsed_query['intent']
        columns = parsed_query['matched_columns']
        
        if df.empty:
            return {"error": "DataFrame is empty."}
            
        # Get purely numeric columns for mathematical operations
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # If no columns were explicitly matched, try to use all numeric columns as a fallback
        target_cols = columns if columns else numeric_cols
        valid_numeric_targets = [col for col in target_cols if col in numeric_cols]
        
        try:
            if intent == 'sum' and valid_numeric_targets:
                result = df[valid_numeric_targets].sum().to_dict()
                return {"operation": "sum", "result": result, "data": df[valid_numeric_targets]}
                
            elif intent == 'average' and valid_numeric_targets:
                result = df[valid_numeric_targets].mean().to_dict()
                return {"operation": "average", "result": result, "data": df[valid_numeric_targets]}
                
            elif intent == 'count':
                # Count the total number of rows
                return {"operation": "count", "result": {"total_rows": len(df)}, "data": df}
                
            elif intent == 'max' and valid_numeric_targets:
                result = df[valid_numeric_targets].max().to_dict()
                return {"operation": "max", "result": result, "data": df[valid_numeric_targets]}
                
            elif intent == 'min' and valid_numeric_targets:
                result = df[valid_numeric_targets].min().to_dict()
                return {"operation": "min", "result": result, "data": df[valid_numeric_targets]}
                
            # If the intent is general or chart just return the data head or specific columns
            subset = df[columns].head(10) if columns else df.head(10)
            return {"operation": "general", "result": "General query, displaying sample data.", "data": subset}
            
        except Exception as e:
            return {"error": f"Error performing analysis: {str(e)}"}
