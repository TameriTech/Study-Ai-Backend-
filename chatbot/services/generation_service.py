import os
from google import genai
from dotenv import load_dotenv
load_dotenv()

class GenerationService:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    def generate_answer(self, context: str, question: str) -> str:
        prompt = f"""
        Use the following study materials to answer the question. 
        If the answer isn't in the materials, say you don't know.
        
        Study materials:
        {context}
        
        Question: {question}
        Answer:
        """
        
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-preview-04-17",
            contents=[prompt]
        )
        # print(response.text.strip())
        return response.text.strip()

generation_service = GenerationService()