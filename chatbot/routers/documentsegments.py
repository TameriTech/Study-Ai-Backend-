from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Query
from sqlalchemy.orm import Session
from database.db import get_db
from database import schemas
from chatbot.services.document_service import document_service
from chatbot.utils.chunking import process_text_into_segments
import os
from io import BytesIO
from PyPDF2 import PdfReader
from typing import Optional

router = APIRouter(prefix="/api/documents", tags=["Chat"])

async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from either PDF or text files"""
    content = await file.read()
    
    if file.content_type == "application/pdf":
        try:
            # Handle PDF files
            pdf_file = BytesIO(content)
            reader = PdfReader(pdf_file)
            text = "\n".join([page.extract_text() for page in reader.pages])
            return text
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text from PDF: {str(e)}"
            )
    else:
        # Handle text files
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="File is not UTF-8 encoded text or PDF"
            )

@router.post("/", response_model=schemas.Document, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    user_id: int,
    title: Optional[str] = Query(None),
    type_document: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        # Extract text from file
        text = await extract_text_from_file(file)
        
        # Determine file type if not provided
        file_type = type_document or file.content_type or os.path.splitext(file.filename)[1][1:]
        
        # Prepare document data
        storage_path = f"documents/{file.filename}"
        document_data = {
            "title": title or os.path.splitext(file.filename)[0],
            "type_document": file_type,
            "original_filename": file.filename,
            "storage_path": storage_path
        }
        
        # Create document
        db_document = document_service.create_document(db, document_data, text, user_id)
        
        # Process into segments
        process_text_into_segments(db, db_document.id_document, text)
        
        return db_document
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )