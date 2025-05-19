import numpy as np
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models import Segment
from chatbot.services.embedding_service import embedding_service

class RetrievalService:
    def get_relevant_segments(self, db: Session, query: str, document_id: Optional[int] = None, top_k: int = 100):
        query_embedding = embedding_service.generate_embedding(query)
        
        segments_query = db.query(Segment)
        
        if document_id:
            segments_query = segments_query.filter(Segment.document_id == document_id)
        
        segments = segments_query.all()
        
        results = []
        for segment in segments:
            if not segment.embedding_vector:
                continue
                
            stored_embedding = np.array(embedding_service.json_to_embedding(segment.embedding_vector))
            similarity = np.dot(query_embedding, stored_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
            )
            
            results.append({
                "segment": segment,
                "score": similarity
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

retrieval_service = RetrievalService()