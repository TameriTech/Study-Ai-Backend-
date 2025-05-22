import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from google.genai.types import HarmCategory, SafetySetting, GenerationConfig

load_dotenv()

class GenerationService:
    def generate_answer(self, context: str, question: str) -> str:
        """Generate an answer to the question based on the context, considering the detected language."""
        
        GEMINI_SYSTEM_INSTRUCTION: str = """Your name is Tameri Study AI, You are an expert academic assistant specialized in 
            providing precise, well-cited answers based on provided context. Always:
            - Maintain an academic tone
            - When necessary, include point forms for better explanation
            - Cite specific context when possible
            - Acknowledge uncertainty when appropriate"""
        
        GEMINI_SAFETY_SETTINGS = [
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold="BLOCK_NONE"),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold="BLOCK_NONE"),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold="BLOCK_NONE"),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold="BLOCK_NONE"),
        ]

        # Create the prompt with a language-specific instruction
        prompt = f"""You are an expert academic assistant. 
            **Language Instruction**:
            Please respond in the language of the question.
            Answer the question using only the information in the context. 
            Avoid generic phrases like "Based on the context"; instead, use natural academic transitions like:
            "The text explains...", "The material shows...", or go straight to the point.
            If the answer is not found in the context, use your knowledge to answer.

            **Context**:
            {context}

            **Question**:
            {question}
            
            **Formatting Instructions**:
             Your answer should be neat and well-organized. Follow these guidelines:
            - Use **headings** in **bold** to introduce different sections of the answer (e.g., "Definitions", "Rules", "Applications").
            - Use **bullet points** or **numbered lists** for any items or steps that need to be enumerated.
            - **Bold** key terms, definitions, and important concepts.
            - Break your answer into clearly defined sections to make it easy to read and understand.
            - Use clear and concise language, and avoid unnecessary fluff.
            - If applicable, include simple visual elements like **emojis** or **diagrams** to make learning engaging.

            **Requirements**:
            - Be precise and academic in your explanations.
            - Directly cite specific parts of the context when relevant.
            - Provide organized and easy-to-read answers with proper formatting.
            - Ensure the tone is formal and consistent with academic writing standards.
        """
        
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_SYSTEM_INSTRUCTION,
                safety_settings=GEMINI_SAFETY_SETTINGS,
            )
        )
        
        return response.text.strip()

# Example usage:
generation_service = GenerationService()