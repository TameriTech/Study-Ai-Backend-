import json
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
MY_OLLAMA_MODEL = os.getenv("MY_OLLAMA_MODEL")  # Default model if not set
OLLAMA_TEXT_MODEL = os.getenv("OLLAMA_TEXT_MODEL")

def generate_from_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_TEXT_MODEL,
                "prompt": prompt,
                "stream": False,  # We want complete response
                # "format": "json"   # Ask for JSON output explicitly
                "temperature": 1
            },
            timeout=300  # 5 minute timeout
        )
        
        response.raise_for_status()  # Will raise HTTPError for 4XX/5XX
        
        result = response.json()
        return result.get("response", "")
        
    except requests.exceptions.RequestException as e:
        print(f"Ollama API error: {str(e)}")
        raise ValueError(f"Failed to generate response: {str(e)}")

def text_generate_from_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MY_OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,  # We want complete response
                # "format": "json"   # Ask for JSON output explicitly
            },
            timeout=300  # 5 minute timeout
        )
        
        response.raise_for_status()  # Will raise HTTPError for 4XX/5XX
        
        result = response.json()
        return result.get("response", "")
        
    except requests.exceptions.RequestException as e:
        print(f"Ollama API error: {str(e)}")
        raise ValueError(f"Failed to generate response: {str(e)}")


