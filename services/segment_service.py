import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime
from database import db
from database.models import Segment

import json

# Initialize embedding model (small but effective)
model = SentenceTransformer('all-MiniLM-L6-v2')

def process_segments(db, document_id: int, text: str, chunk_size: int = 1000) -> int:
    """
    Process raw text into segments with embeddings
    Args:
        db: Database session
        document_id: ID of the parent document
        text: Raw text to process
        chunk_size: Character length for each segment (default: 500)
    Returns:
        Number of segments created
    """
    # Split text into chunks
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    segments_created = 0
    
    for chunk in chunks:
        if not chunk.strip():  # Skip empty chunks
            continue
            
        # Generate embedding (convert text to vector)
        embedding = model.encode(chunk)
        
        # Create segment with placeholder summaries
        segment = Segment(
            document_id=document_id,
            raw_text=chunk,
            created_at=datetime.utcnow()
        )
        
        # Store embedding as JSON string
        segment.embedding_vector = json.dumps(embedding.tolist())
        
        db.add(segment)
        segments_created += 1
    
    db.commit()
    return segments_created

# To retrieve and use embeddings later:
# segment = db.query(Segment).first()
# if segment:
#     embedding = segment.get_embedding()
#     print(f"Embedding shape: {embedding.shape}")  # Should be (384,) for MiniLM-L6