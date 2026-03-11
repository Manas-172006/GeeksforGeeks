import os
import google.generativeai as genai

def initialize_llm():
    """
    Initializes the Gemini client using google-generativeai.
    Loads API key from environment variable or uses fallback.
    Returns the model instance.
    """
    api_key = os.environ.get("GOOGLE_API_KEY", "AIzaSyA0ehyl6ur9dYyntsvghdHuw_PWlLhiqZ4")
    
    if not api_key:
        raise ValueError("Google API Key is missing. Please set GOOGLE_API_KEY environment variable.")
        
    genai.configure(api_key=api_key)
    
    # Use the requested stable model
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    return model

def ask_llm(prompt: str) -> str:
    """
    Sends a prompt to Gemini and returns the response text.
    Handles missing API key or generation errors gracefully.
    """
    try:
        model = initialize_llm()
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "AI service temporarily unavailable. Showing deterministic analysis."
