import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

OPEN_ROUTER_API_URL = os.getenv("OPEN_ROUTER_API_URL")
OPEN_ROUTER_MODEL = os.getenv("OPEN_ROUTER_MODEL")  # Default model if not set
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
def ask_openrouter(prompt, system_prompt=None):
    url = OPEN_ROUTER_API_URL
    headers = {
        "Authorization": OPEN_ROUTER_API_KEY,
        "Content-Type": "application/json",
    }

    # Prepare messages for API request
    messages = []
    
    # Add system prompt if provided
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    # Add user prompt
    messages.append({
        "role": "user",
        "content": prompt
    })

    # Prepare data to be sent to the API
    data = {
        "model": OPEN_ROUTER_MODEL,
        "messages": messages
    }

    try:
        # Make the API request
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}  # Handle exceptions and return the error message


# Fast models
# nousresearch/deephermes-3-mistral-24b-preview:free
# mistralai/mistral-7b-instruct:free