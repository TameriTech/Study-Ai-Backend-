import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

OLLAMA_TEXT_MODEL = os.getenv("OLLAMA_TEXT_MODEL")


def generate_from_ollama(prompt: str) -> str:
    response = requests.post(OLLAMA_API_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    })

    if response.status_code != 200:
        raise Exception("Failed to get response from Ollama")

    return response.json()["response"]

def text_generate_from_ollama(prompt: str) -> str:
    response = requests.post(OLLAMA_API_URL, json={
        "model": OLLAMA_TEXT_MODEL,
        "prompt": prompt,
        "stream": False
    })

    if response.status_code != 200:
        raise Exception("Failed to get response from Ollama")

    return response.json()["response"]


