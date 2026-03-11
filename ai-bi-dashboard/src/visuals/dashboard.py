import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def create_histogram(df: pd.DataFrame, x_col: str, color_col: str = None):
    fig = px.histogram(df, x=x_col, color=color_col, title=f"Histogram of {x_col}")
    _apply_layout(fig)
    return fig

def create_scatter(df: pd.DataFrame, x_col: str, y_col: str, color_col: str = None):
    fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=f"Scatter Plot: {y_col} vs {x_col}")
    _apply_layout(fig)
    return fig

def create_boxplot(df: pd.DataFrame, y_col: str, x_col: str = None, color_col: str = None):
    # Plotly Express usually expects the numeric distribution on y, categories on x
    fig = px.box(df, y=y_col, x=x_col, color=color_col, title=f"Box Plot of {y_col}" + (f" by {x_col}" if x_col else ""))
    _apply_layout(fig)
    return fig

def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str = None, color_col: str = None):
    if y_col:
        fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=f"Bar Chart: {y_col} vs {x_col}")
    else:
        counts = df[x_col].value_counts().reset_index()
        counts.columns = [x_col, 'count']
        fig = px.bar(counts, x=x_col, y='count', title=f"Count of {x_col}")
    _apply_layout(fig)
    return fig

def create_pie_chart(df: pd.DataFrame, names_col: str):
    counts = df[names_col].value_counts().reset_index()
    counts.columns = [names_col, 'count']
    fig = px.pie(counts, names=names_col, values='count', title=f"Pie Chart of {names_col}")
    _apply_layout(fig)
    return fig

def create_correlation_heatmap(df: pd.DataFrame):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        return px.scatter(title="Not enough numeric columns for Correlation Heatmap") # Dummy empty plot
    corr = df[numeric_cols].corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Heatmap")
    _apply_layout(fig)
    return fig

def create_line_chart(df: pd.DataFrame, x_col: str, y_col: str, color_col: str = None):
    fig = px.line(df, x=x_col, y=y_col, color=color_col, title=f"Line Chart: {y_col} over {x_col}")
    _apply_layout(fig)
    return fig

def _apply_layout(fig):
    """Helper to apply standard layout styling"""
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Rockwell")
    )
    return fig

