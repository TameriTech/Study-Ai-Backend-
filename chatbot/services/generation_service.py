import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from google.genai.types import HarmCategory, SafetySetting, GenerationConfig

load_dotenv()

class GenerationService:
    def generate_answer(self, context: str, question: str) -> str:
        GEMINI_SYSTEM_INSTRUCTION: str = """Your name is Tameri Study AI, You are an expert academic assistant specialized in 
            providing precise, well-cited answers based on provided context. Always:
            - Maintain an academic tone
            - When neccessary include point forms for better explanation
            - Cite specific context when possible
            - Acknowledge uncertainty when appropriate"""
        GEMINI_SAFETY_SETTINGS = [
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold="BLOCK_NONE"),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold="BLOCK_NONE"),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold="BLOCK_NONE"),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold="BLOCK_NONE"),
        ]

        prompt = f"""You are an expert academic assistant. 
            Answer the question using only the information in the context. 
            Avoid generic phrases like "Based on the context"; instead, use natural academic transitions like:
            "The text explains...", "The material shows...", or go straight to the point.

            If the answer is not found in the context, respond exactly with:
            ❗ "The answer to your question does not appear in the provided context."

            **Context**:
            {context}

            **Question**:
            {question}

            **Requirements**:
            - Be precise and academic
            - Cite specific parts of the context directly when possible
            - If helpful, include emojis or simple visual elements to make learning fun and memorable
        """

        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-04-17",
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_SYSTEM_INSTRUCTION,
                safety_settings=GEMINI_SAFETY_SETTINGS,
                # max_output_tokens=2000,
                # temperature=0.3,
                # top_p=0.95,
                # top_k=40,
                # stop_sequences=["\n\n"],
                # candidate_count=1
           )
            
        )
        # print(response.text.strip())
        return response.text.strip()

generation_service = GenerationService()