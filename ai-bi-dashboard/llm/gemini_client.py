import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables (e.g., GOOGLE_API_KEY)
load_dotenv()

# Initialize the Gemini model for simple text generation
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key="AIzaSyA0ehyl6ur9dYyntsvghdHuw_PWlLhiqZ4",
    temperature=0.2
)

def ask_llm(context: str, question: str) -> str:
    """
    Asks the LLM a question based on data analysis context.
    Kept strictly simple to avoid unnecessary complexity.
    """
    prompt = f"Data Analysis Context:\n{context}\n\nUser Question:\n{question}\n\nPlease explain the answer clearly and concisely based on the data context."
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"LLM Error: Provide a valid Google AI Studio key! (Details: {str(e)})"
