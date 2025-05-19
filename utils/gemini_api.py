import json
import os
from typing import Dict, List, Optional
from fastapi import HTTPException
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# --- Setup Gemini API ---

genai.configure(api_key=GOOGLE_API_KEY)  # Optional fallback

def generate_gemini_response(
    prompt: str,
    response_type: str = "json",  # "text" or "json"
    system_prompt: str = None
) -> str:
    try:
        import google.generativeai as genai
        model = genai.GenerativeModel(model_name="gemini-2.5-flash-preview-04-17")

        chat = model.start_chat(history=[])
        if system_prompt:
            chat.send_message(system_prompt)

        gen_config = {"response_mime_type": "application/json"} if response_type == "json" else {}

        response = chat.send_message(prompt, generation_config=gen_config)
        return response.text.strip()

    except Exception as e:
        return f"Gemini API error: {str(e)}"


def extract_text_from_image(image: Image.Image) -> str:
    """Extract text using Gemini Vision."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(["Extract all text from this image:", image])
        return response.text.strip()
    except Exception as e:
        raise HTTPException(500, f"Gemini Vision OCR failed: {str(e)}")
    

def validate_and_parse_json(json_str: str) -> Optional[List[Dict]]:
    """Helper function to validate and parse JSON strings"""
    if not json_str or not json_str.strip():
        return None
    
    try:
        parsed = json.loads(json_str)
        if not isinstance(parsed, list):  # Ensure it's a list as expected
            return None
        return parsed
    except json.JSONDecodeError:
        return None
    
def quiz_validate_and_parse_json(json_str: str) -> Optional[List[Dict]]:
    """Helper function to validate and parse JSON strings"""
    if not json_str or not json_str.strip():
        return None
    
    try:
        parsed = json.loads(json_str)
        
        # Debug: Log the parsed response to verify its structure
        print(f"Parsed response: {parsed}")
        
        if not isinstance(parsed, list):  # Ensure it's a list as expected
            print("Response is not a list.")
            return None
        
        # Check if all items are dictionaries with expected keys
        for item in parsed:
            if not isinstance(item, dict) or "question" not in item:
                print("One or more items in the list are invalid.")
                return None
            
        return parsed
    
    except json.JSONDecodeError:
        print("Failed to decode JSON.")
        return None