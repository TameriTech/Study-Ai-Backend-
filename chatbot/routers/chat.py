from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional
from database.db import get_db
from chatbot.services.retrieval_service import retrieval_service
from chatbot.services.generation_service import generation_service
from database.schemas import QuestionRequest, AnswerResponse
from config.email_config import ImageResponse, ImageGenerationRequest

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/generate-image")
async def generate_image(request: ImageGenerationRequest):
    try:
        image_bytes = generation_service.generate_image(request.prompt)
        
        # Return the image directly with proper content type
        return Response(
            content=image_bytes.getvalue(),
            media_type="image/png"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
    try:
        # Retrieve relevant segments
        relevant_segments = retrieval_service.get_relevant_segments(
            db, 
            request.question, 
            request.document_id
        )
        
        # Prepare context
        context = "\n\n".join([seg["segment"].raw_text for seg in relevant_segments])
        sources = [seg["segment"].id_segment for seg in relevant_segments]
        
        # Generate answer
        answer = generation_service.generate_answer(context, request.question)
        
        return {
            "answer": answer,
            "sources": sources,
            "relevant_segments": [seg["segment"].raw_text for seg in relevant_segments]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))