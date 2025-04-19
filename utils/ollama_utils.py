import requests

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def summarize_with_ollama(text: str, model: str = "mistral"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": f"Summarize the following video content and generate 5 questions from it:\n\n{text}",
                "stream": False,
            },
        )
        response.raise_for_status()
        return response.json().get("response", "No response from Ollama")
    except Exception as e:
        raise Exception(f"Ollama summarization failed: {str(e)}")
    

def generate_from_ollama(prompt: str, model: str = "llama2") -> str:
    response = requests.post(OLLAMA_API_URL, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })

    if response.status_code != 200:
        raise Exception("Failed to get response from Ollama")

    return response.json()["response"]


