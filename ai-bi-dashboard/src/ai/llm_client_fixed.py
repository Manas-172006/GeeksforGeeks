import os
import time
from typing import Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import streamlit as st

# Global model instance to avoid repeated initialization
_model_instance = None
_last_init_time = 0
_init_timeout = 30  # seconds

def load_env_variables():
    """Load environment variables from .env file if it exists"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv not available, use system env vars

def initialize_llm(force_reinit: bool = False) -> Optional[genai.GenerativeModel]:
    """
    Initializes the Gemini client with proper error handling and caching.
    Returns cached model instance to avoid repeated initialization.
    """
    global _model_instance, _last_init_time
    
    # Return cached instance if available and recent
    if _model_instance and not force_reinit and (time.time() - _last_init_time) < 300:  # 5 minutes cache
        return _model_instance
    
    try:
        load_env_variables()
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please set the API key.")
        
        genai.configure(api_key=api_key)
        
        # Configure safety settings for reliable responses
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Use stable model with configuration
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            safety_settings=safety_settings,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        _model_instance = model
        _last_init_time = time.time()
        return model
        
    except Exception as e:
        _model_instance = None
        raise Exception(f"Failed to initialize Gemini model: {str(e)}")

def ask_llm(prompt: str, max_retries: int = 3) -> str:
    """
    Sends a prompt to Gemini with robust error handling, retries, and timeouts.
    Returns fallback response if all attempts fail.
    """
    if not prompt or not prompt.strip():
        return "Empty prompt provided."
    
    # Check cache first
    cache_key = f"llm_response_{hash(prompt)}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            model = initialize_llm()
            
            # Generate content with timeout
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                )
            )
            
            # Check if response is valid
            if response and response.text:
                result = response.text.strip()
                # Cache successful response
                st.session_state[cache_key] = result
                return result
            else:
                raise Exception("Empty response from Gemini")
                
        except Exception as e:
            last_error = str(e)
            
            # Handle specific error types
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                return "⚠️ API quota exceeded. Please try again in a few minutes or check your billing settings."
            
            if "permission" in str(e).lower() or "forbidden" in str(e).lower():
                return "⚠️ API permission denied. Please check your API key configuration."
            
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            
            # For other errors, try again
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
    
    # Fallback responses based on error type
    if last_error:
        if "API Key" in last_error:
            return "🔑 Gemini API key not configured. Please set GEMINI_API_KEY in your environment or .env file."
        elif "quota" in last_error.lower():
            return "📊 API quota exceeded. Using basic analysis instead of AI insights."
        elif "timeout" in last_error.lower():
            return "⏰ Request timed out. Please try again with a simpler query."
        else:
            return f"🤖 AI service temporarily unavailable: {last_error}"
    
    return "🤖 AI service temporarily unavailable. Please try again later."

def get_fallback_insight(df_shape: tuple, query_type: str = "general") -> str:
    """Generate basic insights without LLM when Gemini is unavailable"""
    rows, cols = df_shape
    
    if query_type == "summary":
        return f"Dataset contains {rows:,} rows and {cols} columns. Basic statistics are available in the preview section."
    elif query_type == "chart":
        return "Chart generated successfully. For detailed analysis, please check the data summary and statistics."
    else:
        return f"Analysis complete. The dataset has {rows:,} records across {cols} features. Please review the visualizations for insights."
