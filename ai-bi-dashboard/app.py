import streamlit as st

# Main Streamlit application that:
# - loads dataset
# - accepts user prompt
# - calls LLM

def main():
    st.title("AI BI Dashboard")

    # Load dataset
    # TODO: Implement dataset loading

    # Accept user prompt
    user_prompt = st.text_input("Enter your query:")

    if user_prompt:
        # Call LLM
        # TODO: Implement LLM call
        st.write("Response from LLM will appear here.")

if __name__ == "__main__":
    main()