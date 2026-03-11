import streamlit as st
import pandas as pd
import requests
import json
import time

API_BASE_URL = "http://127.0.0.1:8000/api"

# Engines and Utilities
from src.data.loader import load_dataset, safe_load_csv
from src.data.query import QueryEngine
from src.data.analyzer import DataAnalyzer
from src.visuals.charts import ChartGenerator
from src.ai.llm_client_fixed import ask_llm, get_fallback_insight
from src.visuals.dashboard import (
    create_histogram, create_scatter, create_boxplot,
    create_bar_chart, create_pie_chart, create_correlation_heatmap, create_line_chart
)
from src.ai.insights import generate_insights, recommend_charts
from src.utils.data_utils import check_dataset_health
from src.utils.chart_utils import get_chart_options

# Caching decorators for performance
@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_load_dataset(file_path=None):
    """Cached dataset loading"""
    if file_path:
        return pd.read_csv(file_path)
    return load_dataset()

@st.cache_data(ttl=600)  # Cache for 10 minutes
def cached_data_analysis(df, parsed_query):
    """Cached data analysis results"""
    analyzer = DataAnalyzer()
    return analyzer.analyze(df, parsed_query)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_llm_call(prompt: str, cache_key: str = None):
    """Cached LLM calls with fallback"""
    try:
        return ask_llm(prompt)
    except Exception as e:
        return get_fallback_insight((0, 0), "general")

def main():
    st.set_page_config(page_title="AI BI Dashboard", page_icon="📊", layout="wide")

    st.title("📊 AI Business Intelligence Dashboard")

    # Initialize auth state
    if "token" not in st.session_state:
        st.session_state["token"] = None
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None
    if "llm_cache" not in st.session_state:
        st.session_state["llm_cache"] = {}

    # Sidebar for dataset upload
    with st.sidebar:
        st.header("🔐 Authentication")
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

        st.divider()

        st.header("🧭 Navigation")
        app_mode = st.radio("Select View:", ["Chat & Query", "Visual Insights Dashboard"])
        
        st.divider()

        st.header("📁 Dataset Upload")
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

    # Load dataset with caching
    if uploaded_file is not None:
        df = safe_load_csv(uploaded_file)
        st.session_state["df"] = df
    else:
        if "df" not in st.session_state:
            st.session_state["df"] = cached_load_dataset()

    df = st.session_state.get("df")

    if df is not None and not df.empty:
        st.subheader("Preview Data")
        preview_df = df[[c for c in df.columns if "bplist00" not in c and "WebMainResource" not in c and "NSData" not in c]]
        st.dataframe(preview_df.head(), width="stretch")

        st.subheader("Columns")
        st.write(df.columns.tolist())

        st.subheader("Column Types")
        col_types_dict = df.dtypes.to_dict()
        for col, dtype in col_types_dict.items():
            st.write(f"{col} : {dtype}")
            
        st.divider()
    else:
        st.warning("⚠️ No dataset loaded or dataset is empty. Please upload a valid CSV file.")
        st.stop()

    # Initialize components depending on the mode
    if app_mode == "Chat & Query":
        st.markdown("Upload your dataset and ask questions in natural language!")
        
        query_engine = QueryEngine()
        
        # TOP ROW
        col1, col2 = st.columns([2, 1])

        with col1:
            st.header("DATASET OVERVIEW")
            st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
            st.write("**Columns:**", ", ".join(df.columns.tolist()))

        with col2:
            st.header("QUICK STATISTICS")
            if df.select_dtypes(include=[float, int]).shape[1] > 0:
                st.write("**Numeric Columns Summary:**")
                st.dataframe(df.describe(), width='stretch')
            else:
                st.write("No numeric columns found for statistics.")

            # Column info
            st.write("**Column Types:**")
            col_types = df.dtypes.to_dict()
            for col, dtype in col_types.items():
                st.write(f"- {col}: {dtype}")

        st.markdown("---")

        # MIDDLE ROW
        st.header("DATA PREVIEW")
        st.dataframe(df.head(10), width="stretch")

        st.markdown("---")

        # BOTTOM ROW
        st.header("AI QUERY ENGINE")
        user_prompt = st.text_area("Enter your query in natural language:", height=100,
                                   placeholder="e.g., What are the top 5 products by sales? Show me a chart of revenue over time.")

        if st.button("🚀 Analyze", type="primary"):
            if user_prompt.strip():
                with st.spinner("Processing your query..."):
                    # Process query
                    query_columns = df.columns.tolist()
                    parsed_query = query_engine.process_query(user_prompt, query_columns)

                    # Execute Pandas analysis with caching
                    analysis_result = cached_data_analysis(df, parsed_query)
                    
                # Call LLM for explanation with caching and fallback
                context = str(analysis_result.get('result', analysis_result.get('error', 'No numerical result.')))
                try:
                    prompt = f"Data Analysis Context:\n{context}\n\nUser Question:\n{user_prompt}\n\nPlease explain the answer clearly and concisely based on the data context."
                    
                    # Use cache key for LLM calls
                    cache_key = f"query_{hash(prompt)}"
                    if cache_key in st.session_state.llm_cache:
                        llm_response = st.session_state.llm_cache[cache_key]
                    else:
                        llm_response = ask_llm(prompt)
                        st.session_state.llm_cache[cache_key] = llm_response
                        
                except Exception as e:
                    llm_response = get_fallback_insight(df.shape, "query")

                # Chart Generation
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
                        pass # We will fallback to default logic if Plotly fails

                # Generate default Matplotlib Chart if requested or appropriate AND no plotly chart was made
                chart = None
                if not plotly_chart and (parsed_query['is_chart'] or parsed_query['intent'] in ['sum', 'average', 'max', 'min']):
                    chart_generator = ChartGenerator()
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
            st.header("📊 Results")
            
            # Show parsed intent for transparency
            with st.expander("🛠️ Debug Info (Parsed Query)", expanded=False):
                st.write(parsed_query)
                st.write("Raw Analysis Output:")
                st.write(analysis_result)

            st.write("**AI Summary:**")
            st.info(llm_response)

            if plotly_chart:
                st.write("**Visual Representation (Plotly):**")
                st.plotly_chart(plotly_chart, width="stretch")
            elif chart:
                st.write("**Trend Visualization (Matplotlib):**")
                st.pyplot(chart)
        else:
            st.warning("Please enter a query.")
                
    elif app_mode == "Visual Insights Dashboard":
        tab1, tab2, tab3 = st.tabs(["Dataset Overview", "Interactive Charts", "Auto Insights"])
        
        with tab1:
            st.header("📋 Dataset Overview")
            
            # Automated Dataset Health Checks
            health = check_dataset_health(df)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Rows", df.shape[0])
            col2.metric("Columns", df.shape[1])
            missing_total = df.isnull().sum().sum()
            col3.metric("Missing Values", missing_total)
            col4.metric("Duplicates", health['duplicate_rows'])
            
            st.write("**Columns:**", ", ".join(df.columns.tolist()))
            
            st.subheader("Data Preview")
            st.dataframe(df.head(15), width='stretch')
            
            st.subheader("Missing Value Summary")
            if isinstance(health['missing_values'], dict):
                missing_df = pd.DataFrame(list(health['missing_values'].items()), columns=['Column', 'Missing Count'])
                st.dataframe(missing_df, width='stretch')
            else:
                st.success("No missing values in the dataset!")

        with tab2:
            st.header("📈 Interactive Charts")
            
            # Chart recommendation engine
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

                # AI Chart Explanation with caching
                if st.button("Explain this chart"):
                    with st.spinner("Generating explanation..."):
                        chart_config = f"Chart Type: {chart_type}, X-Axis: {x_col}, Y-Axis: {y_col}, Color By: {color_col}"
                        prompt = f"Explain the relationship and meaning of the data shown in this {chart_type}. The chart has {x_col} on the X-axis"
                        if y_col: prompt += f" and {y_col} on the Y-axis."
                        prompt += f" Keep the explanation concise and analytical."
                        
                        cache_key = f"chart_{hash(prompt)}"
                        if cache_key in st.session_state.llm_cache:
                            explanation = st.session_state.llm_cache[cache_key]
                        else:
                            explanation = ask_llm(prompt)
                            st.session_state.llm_cache[cache_key] = explanation
                        
                        st.info(explanation)
                
        with tab3:
            st.header("💡 Auto Insights")
            
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
                    
                    cache_key = f"insights_{hash(prompt)}"
                    if cache_key in st.session_state.llm_cache:
                        ai_insights = st.session_state.llm_cache[cache_key]
                    else:
                        ai_insights = ask_llm(prompt)
                        st.session_state.llm_cache[cache_key] = ai_insights
                    
                    st.write(ai_insights)

if __name__ == "__main__":
    main()
