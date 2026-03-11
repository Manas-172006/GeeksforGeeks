import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables once at module import
load_dotenv()

def initialize_llm():
    """
    Initializes the Gemini client using google-generativeai.
    Loads API key from environment variable GEMINI_API_KEY.
    Returns the model instance.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("API Key is missing. Please set GEMINI_API_KEY environment variable.")
        
    genai.configure(api_key=api_key)
    
    # Use the correct model name for current API
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    return model

def ask_llm(prompt: str) -> str:
    """
    Sends a prompt to Gemini and returns the response text.
    Handles exceptions gracefully.
    """
    try:
        model = initialize_llm()
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"LLM Error: {str(e)}"
