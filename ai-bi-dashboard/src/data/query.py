class QueryEngine:
    def __init__(self):
        # Basic mapping of intents to keywords
        self.keywords = {
            'sum': ['sum', 'total', 'add'],
            'average': ['average', 'mean', 'avg'],
            'count': ['count', 'how many', 'number of'],
            'max': ['maximum', 'max', 'highest', 'most'],
            'min': ['minimum', 'min', 'lowest', 'least'],
            'chart': ['chart', 'graph', 'plot', 'visualize', 'distribution', 'correlation', 'relationship', 'comparison', 'trend']
        }
        
        # Specific chart mappings
        self.chart_keywords = {
            'Histogram': ['distribution', 'spread', 'histogram'],
            'Scatter Plot': ['correlation', 'relationship', 'scatter', 'vs', 'versus'],
            'Bar Chart': ['bar', 'counts', 'category counts', 'comparison'],
            'Pie Chart': ['pie', 'proportion', 'share'],
            'Line Chart': ['trend', 'over time', 'line'],
            'Box Plot': ['box', 'outliers', 'spread by']
        }
        
    def process_query(self, query: str, df_columns: list) -> dict:
        """
        Extracts the basic intent and any matching columns from the user's query.
        """
        query_lower = query.lower()
        
        # Determine intent (defaults to 'general' if none match)
        intent = 'general'
        for key, words in self.keywords.items():
            if any(word in query_lower for word in words):
                intent = key
                break
                
        # Determine if a chart is requested alongside the math intent
        is_chart = any(word in query_lower for word in self.keywords['chart'])
        
        # Determine specific chart type if requested
        chart_type = None
        if is_chart or intent == 'chart':
            for c_type, words in self.chart_keywords.items():
                if any(word in query_lower for word in words):
                    chart_type = c_type
                    is_chart = True
                    break
        
        # Map user input to actual DataFrame columns
        matched_columns = []
        for col in df_columns:
            if col.lower() in query_lower:
                matched_columns.append(col)
                
        return {
            'original_query': query,
            'intent': intent,
            'is_chart': is_chart,
            'chart_type': chart_type,
            'matched_columns': matched_columns
        }
