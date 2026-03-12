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

    # Custom CSS for professional dark analytics dashboard
    st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background: #0E1117;
        color: #E1E5EA;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF;
        font-weight: 600;
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #1C1F26 0%, #2A2D3A 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: #4F8BF9;
    }
    
    .main-header .subtitle {
        font-size: 1.1rem;
        color: #8892A0;
        margin-bottom: 0;
    }
    
    /* Card Containers */
    .card {
        background: #1C1F26;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        border: 1px solid #2A2D3A;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1C1F26 0%, #252830 100%);
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        border: 1px solid #2A2D3A;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4F8BF9;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #8892A0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Sidebar Sections */
    .sidebar-section {
        background: #1C1F26;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #2A2D3A;
    }
    
    /* Data Tables */
    .dataframe {
        background: #1C1F26;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Charts Container */
    .chart-container {
        background: #1C1F26;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #2A2D3A;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #1C1F26;
        border-radius: 8px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #252830;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        color: #8892A0;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: #4F8BF9;
        color: white;
    }
    
    /* Buttons */
    .stButton > button {
        background: #4F8BF9;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #3A7BC8;
        transform: translateY(-1px);
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: #1E3A2F;
        border-left: 4px solid #4CAF50;
    }
    
    .stError {
        background: #3A1E1E;
        border-left: 4px solid #F44336;
    }
    
    .stWarning {
        background: #3A2E1E;
        border-left: 4px solid #FF9800;
    }
    
    .stInfo {
        background: #1E2A3A;
        border-left: 4px solid #2196F3;
    }
    
    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Professional Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 AI Business Intelligence Dashboard</h1>
        <p class="subtitle">Upload datasets, explore insights, and query data using AI.</p>
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
            st.success("File uploaded successfully!")
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
                        st.toast("Dataset saved to your account!")
                        st.session_state["dataset_saved"] = True
                except Exception as e:
                    pass
        else:
            if "dataset_saved" in st.session_state:
                del st.session_state["dataset_saved"]

    # Load dataset
    if uploaded_file is not None:
        df = safe_load_csv(uploaded_file)
        st.session_state["df"] = df
    else:
        if "df" not in st.session_state:
            st.session_state["df"] = load_dataset()

    df = st.session_state.get("df")

    if df is not None and not df.empty:
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
        st.markdown("Upload your dataset and ask questions in natural language!")

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

        # BOTTOM ROW - AI Query Engine
        st.markdown("""
        <div class="card">
            <h2>🤖 AI Query Engine</h2>
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
                </div>
                """, unsafe_allow_html=True)
                st.plotly_chart(plotly_chart, width="stretch")
            elif chart:
                st.markdown("""
                <div class="chart-container">
                    <h3>📈 Trend Visualization</h3>
                </div>
                """, unsafe_allow_html=True)
                st.pyplot(chart)
        else:
            st.warning("Please enter a query.")

    elif app_mode == "Visual Insights Dashboard":
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
                </div>
                """, unsafe_allow_html=True)
                st.plotly_chart(fig, width="stretch")

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
                
            st.divider()
            st.subheader("🧠 Deeper AI Impressions")
            if st.button("Generate Deeper AI Insights"):
                with st.spinner("Analyzing dataset..."):
                    health = check_dataset_health(df)
                    prompt = f"Analyze the following dataset summary and provide 3 key insights in bullet points.\n\nSummary stats:\n{health['summary_text']}"
                    ai_insights = ask_llm(prompt)
                    st.write(ai_insights)

if __name__ == "__main__":
    main()