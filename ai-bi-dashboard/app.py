import streamlit as st
import pandas as pd
import requests
import json

API_BASE_URL = "http://127.0.0.1:8000/api"

# Engines and Utilities
from src.data.loader import load_dataset, safe_load_csv
from src.data.query import QueryEngine
from src.data.analyzer import DataAnalyzer
from src.visuals.charts import ChartGenerator
from src.ai.llm_client import ask_llm
from src.visuals.dashboard import (
    create_histogram, create_scatter, create_boxplot,
    create_bar_chart, create_pie_chart, create_correlation_heatmap, create_line_chart
)
from src.ai.insights import generate_insights, recommend_charts
from src.utils.data_utils import check_dataset_health
from src.utils.chart_utils import get_chart_options

# Main Streamlit application that:
# - allows dynamic dataset upload
# - accepts user prompt
# - calls LLM and generates charts

def main():
    st.set_page_config(page_title="AI BI Dashboard", page_icon="📊", layout="wide")

    # Custom CSS for professional light theme dashboard with dark text
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Source+Sans+Pro:wght@400;600;700&display=swap');
    
    /* GLOBAL TEXT VISIBILITY FIX - All text must be dark and readable */
    body, .main, .stApp, .stAppView {
        color: #000000 !important;
        background: #ffffff !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
    }
    
    p, span, label, div, section, article {
        color: #000000 !important;
    }
    
    .stMarkdown, .stText, .stTitle, .stHeader, .stCaption {
        color: #000000 !important;
    }
    
    /* Force dark text on ALL elements */
    * {
        color: #000000 !important;
    }
    
    /* Override any remaining white text */
    .streamlit-expanderContent *,
    .streamlit-expanderHeader *,
    .card *,
    .metric-card *,
    .chart-container *,
    .sidebar-section * {
        color: #000000 !important;
    }
    
    /* Professional Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    body {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        color: #000000;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: #1f2937;
        font-weight: 700;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    .main-header .subtitle {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Professional Card Containers */
    .card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(226, 232, 240, 0.8);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        transform: translateY(-2px);
    }
    
    .card h2, .card h3, .card h4, .card p, .card div {
        color: #000000 !important;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(226, 232, 240, 0.8);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
        border-radius: 16px 16px 0 0;
    }
    
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Sections */
    .sidebar-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .sidebar-section h3 {
        color: #1f2937 !important;
        font-weight: 600;
        font-family: 'Source Sans Pro', sans-serif;
        margin-bottom: 0.5rem;
    }
    
    /* Modern Sidebar Navigation */
    .css-1lcbm0y {
        background: #1f2937;
        padding: 20px;
        min-height: 100vh;
        border-right: 1px solid #334155;
    }
    
    .css-1lcbm0y .element-container {
        background: #1f2937;
        padding: 0;
        margin: 0;
    }
    
    /* Sidebar Section Cards */
    .sidebar-section {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        border: 1px solid #e5e7eb;
        transition: all 0.2s ease;
    }
    
    .sidebar-section:hover {
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.12);
        transform: translateY(-1px);
    }
    
    .sidebar-section h3 {
        font-size: 18px;
        font-weight: 600;
        color: #111111;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* Navigation Options Styling */
    .stRadio > div > div > label {
        background: #f8fafc;
        border-radius: 8px;
        padding: 10px 12px;
        margin-top: 6px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s ease;
        border: 1px solid #e5e7eb;
        display: block;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        color: #374151;
    }
    
    .stRadio > div > div > label:hover {
        background-color: #e5e7eb;
        border-color: #d1d5db;
        transform: translateX(2px);
    }
    
    .stRadio > div > div > label[data-baseweb="radio"] {
        background-color: #2563eb;
        color: white;
        border-color: #2563eb;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
    }
    
    /* Dataset Upload Area */
    .stFileUploader {
        background: #f9fafb;
        border: 2px dashed #d1d5db;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .stFileUploader:hover {
        border-color: #2563eb;
        background: #eff6ff;
    }
    
    .stFileUploader span {
        color: #374151;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
        padding: 10px 16px;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
        font-size: 14px;
        width: 100%;
        margin-top: 8px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Sidebar Form Elements */
    .stForm {
        background: #ffffff;
        border-radius: 8px;
        padding: 16px;
        margin-top: 12px;
        border: 1px solid #e5e7eb;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 8px 12px;
        font-family: 'Inter', sans-serif;
        color: #374151;
        font-size: 14px;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        outline: none;
    }
    
    /* Success/Error Messages in Sidebar */
    .stSuccess {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 8px;
        padding: 12px;
        font-weight: 500;
        border: none;
        margin-top: 8px;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        border-radius: 8px;
        padding: 12px;
        font-weight: 500;
        border: none;
        margin-top: 8px;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        border-radius: 8px;
        padding: 12px;
        font-weight: 500;
        border: none;
        margin-top: 8px;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border-radius: 8px;
        padding: 12px;
        font-weight: 500;
        border: none;
        margin-top: 8px;
    }
    
    /* Sidebar Spacing */
    .element-container {
        padding: 0 8px !important;
    }
    
    .element-container > div:first-child {
        margin-bottom: 20px;
    }
    
    /* Override default Streamlit sidebar spacing */
    .css-1lcbm0y .stVerticalBlock {
        gap: 20px;
    }
    
    .css-1lcbm0y .stVerticalBlock > div {
        background: transparent;
        border: none;
        padding: 0;
    }
    
    /* Professional Data Tables */
    .dataframe {
        background: #ffffff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(226, 232, 240, 0.8);
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        color: #0f172a;
        font-weight: 600;
        font-family: 'Source Sans Pro', sans-serif;
        position: sticky;
        top: 0;
        z-index: 10;
        padding: 1rem;
        border-bottom: 2px solid #cbd5e1;
    }
    
    .dataframe td {
        color: #1e293b;
        font-family: 'Inter', sans-serif;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .dataframe tr:nth-child(even) {
        background: #f8fafc;
    }
    
    .dataframe tr:hover {
        background: #f1f5f9;
        transition: background 0.2s ease;
    }
    
    /* Professional Charts Container */
    .chart-container {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(226, 232, 240, 0.8);
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        transform: translateY(-2px);
    }
    
    .chart-container h3 {
        color: #0f172a;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
        font-family: 'Source Sans Pro', sans-serif;
        text-align: center;
    }
    
    .chart-container p {
        color: #64748b;
        font-size: 0.95rem;
        text-align: center;
        margin-top: 1rem;
        line-height: 1.6;
    }
    
    /* Professional Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #ffffff;
        border-radius: 12px;
        padding: 0.5rem;
        gap: 0.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(226, 232, 240, 0.8);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f8fafc;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        color: #64748b;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #e2e8f0;
        color: #334155;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Professional Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
        padding: 0.75rem 1.5rem;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        font-size: 0.95rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Primary Button Styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
    }
    
    /* Professional Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-left: 4px solid #22c55e;
        color: #166534;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 500;
    }
    
    .stError {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-left: 4px solid #ef4444;
        color: #dc2626;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 500;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-left: 4px solid #f59e0b;
        color: #d97706;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 500;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-left: 4px solid #3b82f6;
        color: #2563eb;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 500;
    }
    
    /* Professional Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem;
        font-family: 'Inter', sans-serif;
        color: #0f172a;
        transition: all 0.2s ease;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        outline: none;
    }
    
    /* Professional Expanders/Accordions */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        border: 1px solid #cbd5e1;
        color: #0f172a;
        font-weight: 600;
        font-family: 'Source Sans Pro', sans-serif;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
        border-color: #94a3b8;
    }
    
    .streamlit-expanderContent {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
        color: #1f2937;
    }
    
    /* Recommended Charts Section */
    .recommended-charts-list {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .chart-recommendation-item {
        color: #000000 !important;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 500;
        padding: 0.5rem 0.75rem;
        margin: 0.25rem 0;
        background: #ffffff;
        border-radius: 6px;
        border-left: 3px solid #3b82f6;
        transition: all 0.2s ease;
        line-height: 1.5;
    }
    
    .chart-recommendation-item:hover {
        background: #f1f5f9;
        border-left-color: #2563eb;
        transform: translateX(2px);
    }
    
    .recommended-charts-list ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .recommended-charts-list li {
        color: #000000 !important;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 500;
        padding: 0.5rem 0.75rem;
        margin: 0.25rem 0;
        background: #ffffff;
        border-radius: 6px;
        border-left: 3px solid #3b82f6;
        transition: all 0.2s ease;
        line-height: 1.5;
    }
    
    .recommended-charts-list li:hover {
        background: #f1f5f9;
        border-left-color: #2563eb;
        transform: translateX(2px);
    }
    
    /* Fix for st.write content in expanders */
    .streamlit-expanderContent .stMarkdown {
        color: #000000 !important;
    }
    
    .streamlit-expanderContent .stMarkdown p {
        color: #000000 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        margin: 0.5rem 0 !important;
        padding: 0.5rem 0.75rem !important;
        background: #ffffff !important;
        border-radius: 6px !important;
        border-left: 3px solid #3b82f6 !important;
        transition: all 0.2s ease !important;
    }
    
    .streamlit-expanderContent .stMarkdown p:hover {
        background: #f1f5f9 !important;
        border-left-color: #2563eb !important;
        transform: translateX(2px) !important;
    }
    
    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Section Spacing */
    .section-spacing {
        margin-bottom: 2rem;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem 1rem;
            margin-bottom: 1.5rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            margin-bottom: 1rem;
        }
        
        .card {
            margin-bottom: 1rem;
        }
        
        .chart-container {
            padding: 1rem;
        }
        
        .streamlit-expanderHeader {
            font-size: 0.9rem;
            padding: 0.5rem 0.75rem;
        }
        
        .streamlit-expanderContent {
            padding: 0.75rem;
        }
        
        .streamlit-expanderContent .stMarkdown p {
            font-size: 0.85rem !important;
            padding: 0.4rem 0.6rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Professional Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 AI Business Intelligence Dashboard</h1>
        <p class="subtitle">Upload datasets, explore visual insights, and ask AI questions about your data.</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize auth state
    if "token" not in st.session_state:
        st.session_state["token"] = None
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None

    # Sidebar for dataset upload
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <h3>🔐 Authentication</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.session_state["token"]:
            st.success(f"Logged in as {st.session_state['user_email']}")
            if st.button("Logout"):
                st.session_state["token"] = None
                st.session_state["user_email"] = None
                if "current_dataset_id" in st.session_state:
                    del st.session_state["current_dataset_id"]
                st.rerun()
        else:
            auth_mode = st.radio("Access Mode:", ["Guest", "Login", "Sign Up"], horizontal=True)
            if auth_mode == "Login":
                with st.form("login_form"):
                    email = st.text_input("Email")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Login"):
                        try:
                            res = requests.post(f"{API_BASE_URL}/auth/login", data={"username": email, "password": password})
                            if res.status_code == 200:
                                data = res.json()
                                st.session_state["token"] = data.get("access_token")
                                st.session_state["user_email"] = email
                                st.success("Logged in successfully!")
                                st.rerun()
                            else:
                                try:
                                    err = res.json().get("detail", "Invalid credentials.")
                                except Exception:
                                    err = res.text or "Invalid credentials."
                                st.error(err)
                        except Exception as e:
                            st.error(f"Error connecting to backend: {e}")
            elif auth_mode == "Sign Up":
                with st.form("signup_form"):
                    email = st.text_input("Email")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Sign Up"):
                        try:
                            res = requests.post(f"{API_BASE_URL}/auth/signup", json={"email": email, "password": password})
                            if res.status_code == 200:
                                st.success("Signed up successfully! Please login.")
                            else:
                                try:
                                    err = res.json().get("detail", "Signup failed")
                                except Exception:
                                    err = res.text or "Signup failed"
                                st.error(err)
                        except Exception as e:
                            st.error(f"Error connecting to backend: {e}")
            else:
                st.info("Running in Guest Mode. Data will not be saved.")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="sidebar-section">
            <h3>🧭 Navigation</h3>
        </div>
        """, unsafe_allow_html=True)
        app_mode = st.radio("Select View:", ["Chat & Query", "Visual Insights Dashboard"])
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="sidebar-section">
            <h3>📁 Dataset Upload</h3>
        </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

        if uploaded_file is not None:
            st.success(f"✅ '{uploaded_file.name}' uploaded successfully!")
            
            # Load and validate the dataset immediately
            with st.spinner("🔄 Loading and validating dataset..."):
                try:
                    df = safe_load_csv(uploaded_file)
                    st.session_state["df"] = df
                    st.session_state["uploaded_filename"] = uploaded_file.name
                    
                    # Show dataset validation results
                    if not df.empty:
                        st.success(f"✅ Dataset loaded successfully! Found {df.shape[0]:,} rows and {df.shape[1]} columns.")
                        
                        # Show immediate preview in sidebar
                        st.markdown("---")
                        st.markdown("### 📋 Quick Preview")
                        st.dataframe(df.head(3), width="stretch", height=200)
                        
                        # Show column information
                        st.markdown("### 📊 Columns Found")
                        for i, col in enumerate(df.columns[:5]):  # Show first 5 columns
                            st.write(f"• {col}")
                        if len(df.columns) > 5:
                            st.write(f"... and {len(df.columns) - 5} more columns")
                    else:
                        st.error("❌ Failed to load dataset. Please check the file format.")
                        
                except Exception as e:
                    st.error(f"❌ Error loading dataset: {str(e)}")
                    st.session_state["df"] = pd.DataFrame()

            # Save uploaded file temporarily
            file_path = "temp_uploaded.csv"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Save dataset to backend if logged in
            if st.session_state["token"] and "dataset_saved" not in st.session_state:
                try:
                    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                    dataset_data = {"dataset_name": uploaded_file.name, "file_path": file_path}
                    res = requests.post(f"{API_BASE_URL}/datasets/upload-dataset", json=dataset_data, headers=headers)
                    if res.status_code == 200:
                        st.session_state["current_dataset_id"] = res.json()["id"]
                        st.toast("🎉 Dataset saved to your account!")
                        st.session_state["dataset_saved"] = True
                except Exception as e:
                    st.warning(f"⚠️ Could not save to backend: {str(e)}")
        else:
            if "dataset_saved" in st.session_state:
                del st.session_state["dataset_saved"]
            if "uploaded_filename" in st.session_state:
                del st.session_state["uploaded_filename"]

    # Load dataset
    if uploaded_file is not None:
        df = safe_load_csv(uploaded_file)
        st.session_state["df"] = df
    else:
        if "df" not in st.session_state:
            st.session_state["df"] = load_dataset()

    df = st.session_state.get("df")

    if df is not None and not df.empty:
        # Dataset Summary Panel
        st.markdown("""
        <div class="card">
            <h2>📊 Dataset Summary</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        dataset_name = uploaded_file.name if uploaded_file else "Default Dataset"
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{dataset_name}</div>
                <div class="metric-label">Dataset Name</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{df.shape[0]:,}</div>
                <div class="metric-label">Total Rows</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{df.shape[1]}</div>
                <div class="metric-label">Total Columns</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            missing_total = df.isnull().sum().sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{missing_total:,}</div>
                <div class="metric-label">Missing Values</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <h2>📋 Data Preview</h2>
        </div>
        """, unsafe_allow_html=True)

        preview_df = df[[c for c in df.columns if "bplist00" not in c and "WebMainResource" not in c and "NSData" not in c]]
        st.dataframe(preview_df.head(), width="stretch")

        st.markdown("""
        <div class="card">
            <h3>📊 Column Information</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Columns:")
            st.write(df.columns.tolist())

        with col2:
            st.write("**Column Types:")
            col_types_dict = df.dtypes.to_dict()
            for col, dtype in list(col_types_dict.items())[:10]:  # Show first 10
                st.write(f"• {col} : {dtype}")
            if len(col_types_dict) > 10:
                st.write(f"... and {len(col_types_dict) - 10} more")

        st.divider()
    else:
        st.warning("⚠️ No dataset loaded or dataset is empty. Please upload a valid CSV file.")
        st.stop()

    # Initialize components depending on the mode
    if app_mode == "Chat & Query":
        st.markdown("""
        <div class="card">
            <h2>💬 Chat & Query Interface</h2>
            <p>Upload your dataset and ask questions in natural language!</p>
        </div>
        """, unsafe_allow_html=True)

        query_engine = QueryEngine()
        data_analyzer = DataAnalyzer()
        chart_generator = ChartGenerator()

        # TOP ROW - Dataset Overview Cards
        st.markdown("""
        <div class="card">
            <h2>📊 Dataset Overview</h2>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{df.shape[0]:,}</div>
                <div class="metric-label">Total Rows</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{df.shape[1]}</div>
                <div class="metric-label">Columns</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            missing_total = df.isnull().sum().sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{missing_total:,}</div>
                <div class="metric-label">Missing Values</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            duplicate_rows = df.duplicated().sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{duplicate_rows:,}</div>
                <div class="metric-label">Duplicates</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Dataset Details
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("""
            <div class="card">
                <h3>📋 Dataset Details</h3>
                <p><strong>Shape:</strong> {df.shape[0]} rows × {df.shape[1]} columns</p>
                <p><strong>Columns:</strong> {', '.join(df.columns.tolist()[:5])}{'...' if len(df.columns) > 5 else ''}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="card">
                <h3>📈 Quick Statistics</h3>
            </div>
            """, unsafe_allow_html=True)

            if df.select_dtypes(include=[float, int]).shape[1] > 0:
                st.dataframe(df.describe().iloc[[1, 3, 7]], width='stretch')  # Mean, min, max only
            else:
                st.write("No numeric columns found.")

        st.markdown("<br>", unsafe_allow_html=True)

        # MIDDLE ROW - Data Preview
        st.markdown("""
        <div class="card">
            <h2>📋 Data Preview</h2>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(df.head(10), width="stretch")
        
        st.markdown("<br>", unsafe_allow_html=True)

        # COLUMN EXPLORER
        st.markdown("""
        <div class="card">
            <h2>� Column Explorer</h2>
        </div>
        """, unsafe_allow_html=True)
        
        selected_column = st.selectbox("Select a column to explore:", df.columns)
        
        if selected_column:
            col_info_col1, col_info_col2 = st.columns(2)
            
            with col_info_col1:
                st.markdown("""
                <div class="card">
                    <h4>Column Information</h4>
                </div>
                """, unsafe_allow_html=True)
                
                col_dtype = df[selected_column].dtype
                missing_count = df[selected_column].isnull().sum()
                unique_count = df[selected_column].nunique()
                
                st.write(f"**Data Type:** {col_dtype}")
                st.write(f"**Missing Values:** {missing_count:,}")
                st.write(f"**Unique Values:** {unique_count:,}")
                
            with col_info_col2:
                st.markdown("""
                <div class="card">
                    <h4>Basic Statistics</h4>
                </div>
                """, unsafe_allow_html=True)
                
                if pd.api.types.is_numeric_dtype(df[selected_column]):
                    st.write(f"**Mean:** {df[selected_column].mean():.2f}")
                    st.write(f"**Median:** {df[selected_column].median():.2f}")
                    st.write(f"**Std Dev:** {df[selected_column].std():.2f}")
                    st.write(f"**Min:** {df[selected_column].min()}")
                    st.write(f"**Max:** {df[selected_column].max()}")
                else:
                    st.write("*Non-numeric column*")
                    most_common = df[selected_column].value_counts().head(3)
                    st.write("**Top Values:**")
                    for val, count in most_common.items():
                        st.write(f"• {val}: {count:,}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Recommended Questions
        st.markdown("""
        <div class="card">
            <h4>💡 Example Questions</h4>
            <p>Try these sample questions to get started:</p>
            <ul>
                <li>Which class had the highest survival rate?</li>
                <li>Show age distribution</li>
                <li>Compare survival by gender</li>
                <li>What are the top 5 most common values?</li>
                <li>Show correlation between numeric columns</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        user_prompt = st.text_area("Enter your query in natural language:", height=100,
                                   placeholder="e.g., What are the top 5 products by sales? Show me a chart of revenue over time.")

        if st.button("🚀 Analyze", type="primary"):
            if user_prompt.strip():
                with st.spinner("Processing your query..."):
                    # Process query
                    query_columns = df.columns.tolist()
                    parsed_query = query_engine.process_query(user_prompt, query_columns)

                    # Execute Pandas analysis
                    analysis_result = data_analyzer.analyze(df, parsed_query)

                # Call LLM for explanation based on raw analysis result context
                context = str(analysis_result.get('result', analysis_result.get('error', 'No numerical result.')))
                try:
                    # SAFE ADDITION: Formulate prompt for new llm_engine signature
                    prompt = f"Data Analysis Context:\n{context}\n\nUser Question:\n{user_prompt}\n\nPlease explain the answer clearly and concisely based on the data context."
                    llm_response = ask_llm(prompt)
                except Exception as e:
                    llm_response = f"LLM error: {e}"

                # SAFE ADDITION: Natural Language Chart Generation via Plotly
                plotly_chart = None
                if parsed_query.get('chart_type'):
                    c_type = parsed_query['chart_type']
                    cols = parsed_query['matched_columns']

                    try:
                        if c_type == "Histogram" and len(cols) >= 1:
                            plotly_chart = create_histogram(df, cols[0])
                        elif c_type == "Bar Chart" and len(cols) >= 1:
                            y_col = cols[1] if len(cols) >= 2 else None
                            plotly_chart = create_bar_chart(df, cols[0], y_col)
                        elif c_type == "Scatter Plot" and len(cols) >= 2:
                            plotly_chart = create_scatter(df, cols[0], cols[1])
                        elif c_type == "Pie Chart" and len(cols) >= 1:
                            plotly_chart = create_pie_chart(df, cols[0])
                        elif c_type == "Line Chart" and len(cols) >= 2:
                            plotly_chart = create_line_chart(df, cols[0], cols[1])
                        elif c_type == "Box Plot" and len(cols) >= 1:
                            x_col = cols[1] if len(cols) >= 2 else None
                            plotly_chart = create_boxplot(df, cols[0], x_col)
                    except Exception as e:
                        pass  # We will fallback to default logic if Plotly fails

                # Generate default Matplotlib Chart if requested or appropriate AND no plotly chart was made
                chart = None
                if not plotly_chart and (parsed_query['is_chart'] or parsed_query['intent'] in ['sum', 'average', 'max', 'min']):
                    chart = chart_generator.generate_chart(analysis_result, parsed_query['intent'])

            st.success("Analysis complete!")

            # Save query to backend if logged in
            if st.session_state.get("token") and st.session_state.get("current_dataset_id"):
                try:
                    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                    query_data = {
                        "dataset_id": st.session_state["current_dataset_id"],
                        "query_text": user_prompt,
                        "llm_response": llm_response
                    }
                    requests.post(f"{API_BASE_URL}/query", json=query_data, headers=headers)
                    st.toast("Query saved to your account!")
                except Exception:
                    pass

            # Display results
            st.markdown("""
            <div class="card">
                <h2>📊 Analysis Results</h2>
            </div>
            """, unsafe_allow_html=True)

            # Show parsed intent for transparency
            with st.expander("🛠️ Debug Info (Parsed Query)", expanded=False):
                st.write(parsed_query)
                st.write("Raw Analysis Output:")
                st.write(analysis_result)

            st.write("**AI Summary:**")
            st.info(llm_response)

            if plotly_chart:
                st.markdown("""
                <div class="chart-container">
                    <h3>📈 Visual Representation</h3>
                    <p>This chart visualizes the data based on your query about "{user_prompt[:50]}{'...' if len(user_prompt) > 50 else ''}".</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Chart Grid Layout
                chart_col1, chart_col2 = st.columns(2)
                with chart_col1:
                    st.plotly_chart(plotly_chart, width="stretch")
                
                with chart_col2:
                    st.markdown("""
                    <div class="card">
                        <h4>📊 Chart Analysis</h4>
                        <p><strong>Query:</strong> {user_prompt}</p>
                        <p><strong>Chart Type:</strong> {parsed_query.get('chart_type', 'Auto-generated')}</p>
                        <p><strong>Columns Used:</strong> {', '.join(parsed_query.get('matched_columns', []))}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Export Options
                st.markdown("""
                <div class="card">
                    <h4>💾 Export Options</h4>
                </div>
                """, unsafe_allow_html=True)
                
                export_col1, export_col2 = st.columns(2)
                
                with export_col1:
                    if st.button("📥 Download Chart as PNG"):
                        st.info("Chart download feature coming soon!")
                
                with export_col2:
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download Data as CSV",
                        data=csv_data,
                        file_name="analysis_data.csv",
                        mime="text/csv"
                    )
            elif chart:
                st.markdown("""
                <div class="chart-container">
                    <h3>📈 Trend Visualization</h3>
                    <p>This chart shows the trend analysis based on your query about "{user_prompt[:50]}{'...' if len(user_prompt) > 50 else ''}".</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Chart Grid Layout
                chart_col1, chart_col2 = st.columns(2)
                with chart_col1:
                    st.pyplot(chart)
                
                with chart_col2:
                    st.markdown("""
                    <div class="card">
                        <h4>📊 Chart Analysis</h4>
                        <p><strong>Query:</strong> {user_prompt}</p>
                        <p><strong>Analysis Type:</strong> {parsed_query.get('intent', 'General analysis')}</p>
                        <p><strong>Columns:</strong> {', '.join(parsed_query.get('matched_columns', []))}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Export Options
                st.markdown("""
                <div class="card">
                    <h4>💾 Export Options</h4>
                </div>
                """, unsafe_allow_html=True)
                
                export_col1, export_col2 = st.columns(2)
                
                with export_col1:
                    if st.button("📥 Download Chart as PNG"):
                        st.info("Chart download feature coming soon!")
                
                with export_col2:
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download Data as CSV",
                        data=csv_data,
                        file_name="trend_data.csv",
                        mime="text/csv"
                    )
        else:
            st.warning("Please enter a query.")

    elif app_mode == "Visual Insights Dashboard":
        st.markdown("""
        <div class="card">
            <h2>📈 Visual Insights Dashboard</h2>
            <p>Explore your data through interactive charts and automatic insights.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["Dataset Overview", "Interactive Charts", "Auto Insights"])

        with tab1:
            st.markdown("""
            <div class="card">
                <h2>📋 Dataset Overview</h2>
            </div>
            """, unsafe_allow_html=True)

            # Dataset Health Checks
            health = check_dataset_health(df)

            # Metrics Cards
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{df.shape[0]:,}</div>
                    <div class="metric-label">Rows</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{df.shape[1]}</div>
                    <div class="metric-label">Columns</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                missing_total = df.isnull().sum().sum()
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{missing_total:,}</div>
                    <div class="metric-label">Missing Values</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{health['duplicate_rows']:,}</div>
                    <div class="metric-label">Duplicates</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Dataset Info
            st.markdown("""
            <div class="card">
                <h3>📊 Dataset Information</h3>
                <p><strong>Columns:</strong> {', '.join(df.columns.tolist())}</p>
            </div>
            """, unsafe_allow_html=True)

            # Data Preview
            st.markdown("""
            <div class="card">
                <h3>👁️ Data Preview</h3>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(df.head(15), width='stretch')

            # Missing Values Summary
            st.markdown("""
            <div class="card">
                <h3>⚠️ Missing Value Summary</h3>
            </div>
            """, unsafe_allow_html=True)
            if isinstance(health['missing_values'], dict):
                missing_df = pd.DataFrame(list(health['missing_values'].items()), columns=['Column', 'Missing Count'])
                st.dataframe(missing_df, width='stretch')
            else:
                st.success("No missing values in the dataset!")

        with tab2:
            st.markdown("""
            <div class="card">
                <h2>📈 Interactive Charts</h2>
            </div>
            """, unsafe_allow_html=True)

            # SAFE ADDITION: Chart recommendation engine
            recommendations = recommend_charts(df)
            if recommendations:
                with st.expander("💡 Recommended Charts", expanded=False):
                    for rec in recommendations:
                        st.write(f"- {rec}")

            chart_types = get_chart_options()

            col_chart_type, col_x, col_y, col_color = st.columns(4)
            with col_chart_type:
                chart_type = st.selectbox("Select Chart Type", chart_types)

            with col_x:
                x_col = st.selectbox("X-axis Column (or Target)", df.columns)

            with col_y:
                y_options = ["None"] + list(df.columns)
                y_col = st.selectbox("Y-axis Column (Optional)", y_options)
                y_col = None if y_col == "None" else y_col

            with col_color:
                color_options = ["None"] + list(df.columns)
                color_col = st.selectbox("Color By (Optional)", color_options)
                color_col = None if color_col == "None" else color_col

            st.divider()

            fig = None
            try:
                if chart_type == "Histogram":
                    fig = create_histogram(df, x_col, color_col)
                elif chart_type == "Box Plot":
                    fig = create_boxplot(df, y_col=x_col, x_col=y_col, color_col=color_col)
                elif chart_type == "Bar Chart":
                    fig = create_bar_chart(df, x_col, y_col, color_col)
                elif chart_type == "Scatter Plot":
                    if y_col:
                        fig = create_scatter(df, x_col, y_col, color_col)
                    else:
                        st.warning("Scatter plot requires both X and Y columns.")
                elif chart_type == "Pie Chart":
                    fig = create_pie_chart(df, x_col)
                elif chart_type == "Line Chart":
                    if y_col:
                        fig = create_line_chart(df, x_col, y_col, color_col)
                    else:
                        st.warning("Line chart requires both X and Y columns.")
                elif chart_type == "Correlation Heatmap":
                    fig = create_correlation_heatmap(df)
            except Exception as e:
                st.error(f"Error generating chart: {e}")

            if fig is not None:
                st.markdown("""
                <div class="chart-container">
                    <h3>📊 Generated Chart</h3>
                    <p>This {chart_type.lower()} visualizes the relationship between {x_col} and {y_col if y_col else 'data distribution'}.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Chart Grid Layout
                chart_col1, chart_col2 = st.columns(2)
                with chart_col1:
                    st.plotly_chart(fig, width="stretch")
                
                with chart_col2:
                    st.markdown("""
                    <div class="card">
                        <h4>📊 Chart Details</h4>
                        <p><strong>Type:</strong> {chart_type}</p>
                        <p><strong>X-Axis:</strong> {x_col}</p>
                        <p><strong>Y-Axis:</strong> {y_col if y_col else 'N/A'}</p>
                        <p><strong>Color By:</strong> {color_col if color_col else 'N/A'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Export Options
                st.markdown("""
                <div class="card">
                    <h4>💾 Export Options</h4>
                </div>
                """, unsafe_allow_html=True)
                
                export_col1, export_col2 = st.columns(2)
                
                with export_col1:
                    if st.button("📥 Download Chart as PNG"):
                        st.info("Chart download feature coming soon!")
                
                with export_col2:
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download Data as CSV",
                        data=csv_data,
                        file_name="chart_data.csv",
                        mime="text/csv"
                    )

                # Save chart to backend if logged in
                if st.session_state.get("token") and st.session_state.get("current_dataset_id"):
                    if st.button("Save Chart to Dashboard"):
                        try:
                            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                            chart_data = {
                                "dataset_id": st.session_state["current_dataset_id"],
                                "chart_config_json": fig.to_json()
                            }
                            res = requests.post(f"{API_BASE_URL}/charts/save-chart", json=chart_data, headers=headers)
                            if res.status_code == 200:
                                st.success("Chart saved to your account!")
                        except Exception as e:
                            st.error(f"Failed to save chart: {e}")

                # SAFE ADDITION: AI Chart Explanation
                if st.button("Explain this chart"):
                    with st.spinner("Generating explanation..."):
                        chart_config = f"Chart Type: {chart_type}, X-Axis: {x_col}, Y-Axis: {y_col}, Color By: {color_col}"
                        prompt = f"Explain the relationship and meaning of the data shown in this {chart_type}. The chart has {x_col} on the X-axis"
                        if y_col: prompt += f" and {y_col} on the Y-axis."
                        prompt += f" Keep the explanation concise and analytical."

                        explanation = ask_llm(prompt)
                        st.info(explanation)

        with tab3:
            st.markdown("""
            <div class="card">
                <h2>💡 Auto Insights</h2>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Generating insights..."):
                insights = generate_insights(df)

            if insights:
                for insight in insights:
                    st.markdown(f"- {insight}")
            else:
                st.info("No notable insights found for this dataset.")
                
            st.markdown("""
            <div class="card">
                <h3>🧠 Deeper AI Impressions</h3>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Generate Deeper AI Insights"):
                with st.spinner("Analyzing dataset..."):
                    health = check_dataset_health(df)
                    prompt = f"Analyze the following dataset summary and provide 3 key insights in bullet points.\n\nSummary stats:\n{health['summary_text']}"
                    ai_insights = ask_llm(prompt)
                    st.write(ai_insights)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #8892A0; border-top: 1px solid #2A2D3A; margin-top: 3rem;">
        <p>🚀 AI Business Intelligence Dashboard — Hackathon Demo</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">Built with Streamlit, Python, and AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()