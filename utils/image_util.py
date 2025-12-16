import os
import io
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from PIL import Image
from database.models import Document
from services.course_service import create_course
from services.segment_service import process_segments
from utils.gemini_api import generate_gemini_response, extract_text_from_image

# Configuration Constants
TEMP_IMAGE_DIR = "temp_files/images"
MAX_FILE_SIZE_MB = 10
MAX_DIMENSION = 1500
ALLOWED_CONTENT_TYPE_PREFIX = "image/"

def ensure_directories():
    """Ensure necessary directories exist."""
    os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

def compress_image_if_needed(image_bytes: bytes) -> bytes:
    """Compress image if dimensions exceed MAX_DIMENSION."""
    image = Image.open(io.BytesIO(image_bytes))
    if image.width > MAX_DIMENSION or image.height > MAX_DIMENSION:
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
        compressed_io = io.BytesIO()
        image.save(compressed_io, format="JPEG", quality=85)
        compressed_io.seek(0)
        return compressed_io.read()
    return image_bytes

async def extract_and_save_image(db: Session, file: UploadFile, user_id: int, instruction: str) -> dict:
    ensure_directories()

    # Validate content type
    if not file.content_type.startswith(ALLOWED_CONTENT_TYPE_PREFIX):
        raise HTTPException(400, "Only image files are allowed")

    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)

    # Resize/compress if needed
    if file_size_mb > MAX_FILE_SIZE_MB:
        contents = compress_image_if_needed(contents)

    image = Image.open(io.BytesIO(contents))

    # OCR with Gemini
    extracted_text = extract_text_from_image(image)

    if not extracted_text:
        raise HTTPException(422, "No text could be extracted from the image")

    # Save image locally
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    storage_path = os.path.join(TEMP_IMAGE_DIR, safe_filename)

    with open(storage_path, "wb") as f:
        f.write(contents)

    # Save to database
    db_document = Document(
        title=file.filename,
        type_document="image",
        original_filename=file.filename,
        storage_path=storage_path,
        original_text=extracted_text,
        uploaded_at=datetime.utcnow(),
        user_id=user_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Create course and process segments
    course = create_course(db, db_document.id_document, file.filename, extracted_text, instruction)
    process_segments(db, db_document.id_document, extracted_text)

    return {
        "document_id": db_document.id_document,
        "user_id": user_id,
        "cours_info": {"id": course.id_course},
        "filename": file.filename,
        "storage_path": storage_path,
        "extracted_text": extracted_text,
        "message": "IMAGE processed successfully with Gemini OCR and text segmentation"
    }
