import streamlit as st
from dataset_loader import load_dataset

# Main Streamlit application that:
# - loads dataset
# - accepts user prompt
# - calls LLM

def main():
    st.title("AI Business Intelligence Dashboard")

    # Load dataset
    df = load_dataset()

    # Display dataset info
    st.write(f"Dataset shape: {df.shape}")
    st.write("Columns:", list(df.columns))
    st.dataframe(df.head())

    # Accept user prompt
    user_prompt = st.text_input("Enter your query:")

    if user_prompt:
        # Call LLM
        # TODO: Implement LLM call
        st.write("Response from LLM will appear here.")

if __name__ == "__main__":
    main()