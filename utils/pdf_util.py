import os
import fitz  # PyMuPDF
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from database.models import Document
from services.course_service import create_course
from services.segment_service import process_segments
from utils.ollama_utils import text_generate_from_ollama

# Ensure the temp_files/pdf directory exists
os.makedirs("temp_files/pdf", exist_ok=True)

async def extract_and_save_pdf(db: Session, file: UploadFile, user_id: int) -> dict:
    """
    Process PDF file: save to storage, extract text, create database records,
    and generate text segments with embeddings.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Create storage path with timestamp to prevent name collisions
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    storage_path = f"temp_files/pdf/{safe_filename}"

    # Save the PDF file
    contents = await file.read()
    with open(storage_path, "wb") as f:
        f.write(contents)

    # Extract text from PDF
    text = ""
    with fitz.open(storage_path) as pdf:
        for page in pdf:
            text += page.get_text()

    summary_prompt = f"""
    Here is a text from a PDF document:
    ---
    {text}
    ---
    Summarize the text above for revision purpose.
    """
    summary_text = text_generate_from_ollama(summary_prompt)

    simplify_prompt = f"""
    Here is a text from a PDF document:
    ---
    {text}
    ---
    Simplify the text above for purpose of better undersatanding.
    """
    simplified_text = text_generate_from_ollama(simplify_prompt)
    
    # Create document record in database
    db_document = Document(
        title=file.filename,
        type_document="pdf",
        original_filename=file.filename,
        storage_path=storage_path,
        original_text = text,
        uploaded_at=datetime.utcnow(),
        user_id=user_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Process text into segments with embeddings
    create_course(db, db_document.id_document,file.filename, text, simplified_text, summary_text)
    process_segments(db, db_document.id_document, text)

    return {
        "document_id": db_document.id_document,
        "user_id": user_id,
        "filename": file.filename,
        "storage_path": storage_path,
        "extracted_text": text[:100],
        "message": "PDF processed successfully with text segmentation and embeddings"
    }