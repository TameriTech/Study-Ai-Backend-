import json
import os
from typing import Dict, List, Optional
from fastapi import HTTPException
from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv
load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# --- Setup Gemini API ---

genai.Client(api_key=GOOGLE_API_KEY)  # Optional fallback

def generate_gemini_response(
    prompt: str,
    response_type: str = "json",  # "text" or "json"
    system_prompt: str = None
) -> str:
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        config_params = {}
        if response_type == "json":
            config_params["response_mime_type"] = "application/json"
        if system_prompt:
            config_params["system_instruction"] = system_prompt
            
        config = types.GenerateContentConfig(**config_params) if config_params else None
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=[prompt],
            config=config
        )
        return response.text.strip()

    except Exception as e:
        return f"Gemini API error: {str(e)}"

def extract_text_from_image(image: Image.Image) -> str:
    """Extract text using Gemini Vision."""
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=["Extract all text from this image:", image]
        )
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
        # print(f"Parsed response: {parsed}")
        
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