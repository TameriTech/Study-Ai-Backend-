from datetime import datetime
from chatbot.services.embedding_service import embedding_service
from database.models import Segment
from typing import Optional

def process_text_into_segments(
    db,
    document_id: int,
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> int:
    """
    Process text into segments with optional overlap
    """
    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size")
    
    segments_created = 0
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        if not chunk.strip():
            start = end - overlap  # Move forward
            continue
            
        embedding = embedding_service.generate_embedding(chunk)
        
        segment = Segment(
            document_id=document_id,
            raw_text=chunk,
            embedding_vector=embedding_service.embedding_to_json(embedding),
            created_at=datetime.utcnow()
        )
        
        db.add(segment)
        segments_created += 1
        start = end - overlap  # Apply overlap
    
    db.commit()
    return segments_created