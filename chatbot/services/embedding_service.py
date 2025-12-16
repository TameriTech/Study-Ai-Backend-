import numpy as np
import json
from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def generate_embedding(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
    
    def embedding_to_json(self, embedding: List[float]) -> str:
        return json.dumps(embedding)
    
    def json_to_embedding(self, json_str: str) -> List[float]:
        return json.loads(json_str)

embedding_service = EmbeddingService()