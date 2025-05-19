from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyBk2XlW782njqe0CqGfO8iw6exCvX3VECQ")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a cat. Your name is Neko."),
    contents="Hello there"
)

print(response.text)