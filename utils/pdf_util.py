import os
import fitz  # PyMuPDF
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from database.models import Document
from services.course_service import create_course
from services.segment_service import process_segments
from utils.gemini_api import generate_gemini_response

# Ensure the temp_files/pdf directory exists
os.makedirs("temp_files/pdf", exist_ok=True)

async def extract_and_save_pdf(db: Session, file: UploadFile, user_id: int) -> dict:
    """
    Process PDF file: save to storage, extract text (limited to 5000 words),
    create database records, and generate text segments with embeddings.
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

    # Extract text from PDF with word limit
    text = ""
    word_count = 0
    word_limit = 5000
    limit_exceeded = False
    
    with fitz.open(storage_path) as pdf:
        for page in pdf:
            page_text = page.get_text()
            words = page_text.split()
            remaining_words = word_limit - word_count
            
            if remaining_words <= 0:
                limit_exceeded = True
                break
                
            # Add only the words we still need
            needed_words = words[:remaining_words]
            text += " ".join(needed_words) + " "
            word_count += len(needed_words)
            
            if word_count >= word_limit:
                limit_exceeded = True
                break

    # Clean up the text by removing extra spaces
    text = ' '.join(text.split())

    # Prepare the status message
    if limit_exceeded:
        processing_message = f"PDF processed successfully with text limited to {word_limit} words (original contained more text)"
    else:
        processing_message = f"PDF processed successfully with {word_count} words"

    # Generate prompts with the limited text
    summary_prompt = f"""
    Here is a text from a PDF document:
    ---
    {text}
    ---
    Summarize the text above for revision purpose.
    Make to sammurize in the language of the provided text
    """
   
    simplify_prompt = f"""
    Here is a text from a PDF document:
    ---
    {text}
    ---
    Simplify the text above for purpose of better understanding.
    Make to simplied in the language of the provided text
    """

    # Generate summaries using Gemini
    summary_text = generate_gemini_response(
        prompt=summary_prompt,
        response_type="text",
        system_prompt="You are a TEXT summarization assistant."
    )
    simplified_text = generate_gemini_response(
        prompt=simplify_prompt,
        response_type="text",
        system_prompt="You are a TEXT simplification assistant."
    )

    # Create document record in database
    db_document = Document(
        title=file.filename,
        type_document="pdf",
        original_filename=file.filename,
        storage_path=storage_path,
        original_text=text,
        uploaded_at=datetime.utcnow(),
        user_id=user_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Process text into segments with embeddings
    course = create_course(db, db_document.id_document, file.filename, text, simplified_text, summary_text)
    process_segments(db, db_document.id_document, text)

    return {
        "document_id": db_document.id_document,
        "user_id": user_id,
        "filename": file.filename,
        "course_info": {"id": course.id_course},
        "storage_path": storage_path,
        "extracted_text": text[:100],
        "word_count": word_count,
        "limit_exceeded": limit_exceeded,  # Added this flag to the response
        "message": processing_message
    }