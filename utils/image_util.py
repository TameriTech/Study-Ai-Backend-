import os
import io
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from PIL import Image
import pytesseract
from database.models import Document
from services.course_service import create_course
from services.segment_service import process_segments
# from utils.ollama_utils import generate_from_ollama
from fastapi import UploadFile, HTTPException
from PIL import Image
import pytesseract
import io
from utils.gemini_api import generate_gemini_response
# from utils.open_router import ask_openrouter  # Import the ask_openrouter function


os.makedirs("temp_files/images", exist_ok=True)

async def extract_and_save_image(db: Session, file: UploadFile, user_id: int) -> dict:
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Only image files are allowed")

    # Save image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    storage_path = f"temp_files/images/{safe_filename}"
    
    contents = await file.read()
    with open(storage_path, "wb") as f:
        f.write(contents)

    # Extract text
    try:
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image).strip()
    except Exception as e:
        raise HTTPException(500, f"OCR failed: {str(e)}")

    summary_prompt = f"""
    Here is a text from a PDF document:
    ---
    {text[:100]}
    ---
    Summarize the text above for revision purpose.
    """
   
    simplify_prompt = f"""
    Here is a text from a PDF document:
    ---
    {text[:100]}
    ---
    Simplify the text above for purpose of better undersatanding.
    """

    # summary_text = generate_from_ollama(summary_prompt)
    # simplified_text = generate_from_ollama(simplify_prompt)

    # summary_content = ask_openrouter(summary_prompt, system_prompt="You are a TEXT summarization assistant.")
    # simplified_content = ask_openrouter(simplify_prompt, system_prompt="You are a TEXT simplification assistant.")

    # summary_text = summary_content['choices'][0]['message']['content']
    # simplified_text = simplified_content['choices'][0]['message']['content']

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
    # print(f"Summary content:\n{summary_text}")
    # print(f"\nSimplified content:\n{simplified_text}")

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
    course = create_course(db, db_document.id_document,file.filename, text, simplified_text, summary_text)
    process_segments(db, db_document.id_document, text)

    return {
        "document_id": db_document.id_document,
        "user_id": user_id,
        "cours_info": {"id": course.id_course},
        "filename": file.filename,
        "storage_path": storage_path,
        "extracted_text": text[:100],
        "message": "IMAGE processed successfully with text segmentation and embeddings"
    }

