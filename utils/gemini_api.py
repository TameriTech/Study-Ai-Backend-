import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# --- Setup Gemini API ---
genai.configure(api_key=GOOGLE_API_KEY)  # Optional fallback


def generate_gemini_response(
    prompt: str,
    response_type: str = "text",  # "text" or "json"
    system_prompt: str = None
) -> str:
    """
    Generate a response from the Gemini model.

    Args:
        prompt (str): User prompt to send.
        model_name (str): Gemini model variant.
        response_type (str): "text" or "json".
        system_prompt (str, optional): Optional system-level instructions.

    Returns:
        str: Raw text or JSON string from the model.
    """
    # Init model
    model = genai.GenerativeModel(model_name="gemini-2.5-flash-preview-04-17")

    # Start chat with optional system prompt
    chat = model.start_chat(history=[])
    if system_prompt:
        chat.send_message(system_prompt)

    # Configure response MIME type for JSON enforcement
    gen_config = {"response_mime_type": "application/json"} if response_type == "json" else {}

    # Send user prompt
    response = chat.send_message(prompt, generation_config=gen_config)

    return response.text
