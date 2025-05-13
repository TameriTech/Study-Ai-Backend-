import os
import subprocess
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from database.models import Document
from services.course_service import create_course
from services.segment_service import process_segments
import pytesseract
from PIL import Image
import tempfile
from utils.gemini_api import generate_gemini_response
# from utils.open_router import ask_openrouter  # Import the ask_openrouter function
# from utils.ollama_utils import generate_from_ollama, text_generate_from_ollama

os.makedirs("temp_files/videos", exist_ok=True)

async def extract_and_save_video(db: Session, file: UploadFile, user_id: int, frames_per_second: int = 1) -> dict:
    """
    Process video file using FFmpeg and Tesseract OCR with 5000 word limit
    """
    # Validate file type
    allowed_extensions = ('.mp4', '.mov', '.avi', '.mkv')
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(400, f"Only {', '.join(allowed_extensions)} files are allowed")

    # Save video
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    storage_path = f"temp_files/videos/{safe_filename}"
    
    contents = await file.read()
    with open(storage_path, "wb") as f:
        f.write(contents)

    # Extract frames using FFmpeg
    all_text = ""
    word_count = 0
    word_limit = 5000
    limit_exceeded = False
    
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Extract frames
            frame_pattern = os.path.join(tmp_dir, "frame_%04d.png")
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", storage_path,
                "-vf", f"fps={frames_per_second}",
                "-q:v", "2",
                frame_pattern
            ]
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)

            # Process each frame until word limit is reached
            for frame_file in sorted(os.listdir(tmp_dir)):
                if word_count >= word_limit:
                    limit_exceeded = True
                    break
                    
                if frame_file.startswith("frame_") and frame_file.endswith(".png"):
                    frame_path = os.path.join(tmp_dir, frame_file)
                    try:
                        frame_text = pytesseract.image_to_string(Image.open(frame_path)).strip()
                        if frame_text:
                            # Calculate remaining words we can add
                            frame_words = frame_text.split()
                            remaining_words = word_limit - word_count
                            
                            if remaining_words <= 0:
                                limit_exceeded = True
                                break
                                
                            # Add only the needed words from this frame
                            needed_words = frame_words[:remaining_words]
                            frame_text_to_add = " ".join(needed_words)
                            all_text += f"\nFRAME {frame_file}:\n{frame_text_to_add}\n"
                            word_count += len(needed_words)
                            
                    except Exception as e:
                        print(f"OCR failed on {frame_file}: {str(e)}")
                        continue

    except subprocess.CalledProcessError as e:
        raise HTTPException(500, f"FFmpeg failed: {e.stderr.decode()}")
    
    # Clean up the text
    all_text = ' '.join(all_text.split())
    
    # Prepare the status message
    processing_message = "VIDEO processed successfully with text segmentation and embeddings"
    if limit_exceeded:
        processing_message = f"VIDEO processed with text limited to {word_limit} words (some content may be truncated)"

    summary_prompt = f"""
    Here is a text extracted from a video:
    ---
    {all_text}
    ---
    Summarize the text above for revision purpose.
    """
   
    simplify_prompt = f"""
    Here is a text extracted from a video:
    ---
    {all_text}
    ---
    Simplify the text above for purpose of better understanding.
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
        type_document="video",  # Changed from "pdf" to "video"
        original_filename=file.filename,
        storage_path=storage_path,
        original_text=all_text,
        uploaded_at=datetime.utcnow(),
        user_id=user_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Process text into segments with embeddings
    course = create_course(db, db_document.id_document, file.filename, all_text, simplified_text, summary_text)
    process_segments(db, db_document.id_document, all_text)

    return {
        "document_id": db_document.id_document,
        "user_id": user_id,
        "course_info": {"id": course.id_course},  # Fixed typo from "cours_info"
        "filename": file.filename,
        "storage_path": storage_path,
        "extracted_text": all_text[:100],
        "word_count": word_count,
        "message": processing_message
    }