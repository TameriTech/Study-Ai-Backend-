import os
import subprocess
from datetime import datetime
import time
import traceback
import uuid
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from database.models import Document
from services.course_service import create_course
from services.segment_service import process_segments
import tempfile
from utils.gemini_api import generate_gemini_response
from pydub import AudioSegment
import whisper
import logging
from fastapi import HTTPException
import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

os.makedirs("temp_files/videos", exist_ok=True)
os.makedirs("temp_files/videos/audios", exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def extract_and_save_video(db: Session, file: UploadFile, user_id: int) -> dict:
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes
    
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File is too large. Maximum allowed size is 20MB.")

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            allowed_extensions = ('.mp4', '.mov', '.avi', '.mkv')
            if not file.filename.lower().endswith(allowed_extensions):
                raise HTTPException(400, f"Only {', '.join(allowed_extensions)} files are allowed")

            # Save video
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
            audio_filename = f"{timestamp}_audio.mp3"
            
            video_path = os.path.abspath(os.path.normpath(f"temp_files/videos/{video_filename}"))
            audio_path = os.path.abspath(os.path.normpath(f"temp_files/videos/audios/{audio_filename}"))
            
            logger.info(f"Writing video file to: {video_path}")
            with open(video_path, "wb") as buffer:
                buffer.write(await file.read())

            # Convert video to audio using pydub
            try:
                logger.info("Extracting audio from video...")
                audio = AudioSegment.from_file(video_path)
                audio.export(audio_path, format="mp3")
                logger.info(f"Audio extracted successfully to: {audio_path}")
            except Exception as e:
                logger.error(f"Audio extraction failed: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Audio extraction failed: {str(e)}. Ensure FFmpeg is installed.")

            # Transcribe Audio to Text
            logger.info("Loading Whisper model...")
            try:
                whisper_model = whisper.load_model("base", device="cpu")
                logger.info("Starting transcription...")
                transcription = whisper_model.transcribe(audio_path)
                video_text = transcription["text"]
                logger.info(f"Transcript extracted successfully! Length: {len(video_text)} chars")
            except Exception as e:
                logger.error(f"Whisper transcription failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

            # Generate prompts
            logger.info("Generating Gemini prompts...")
            summary_prompt = f"""
            Here is a text extracted from a video:
            ---
            {video_text}
            ---
            Summarize the text above for revision purpose.
            """
            
            simplify_prompt = f"""
            Here is a text extracted from a video:
            ---
            {video_text}
            ---
            Simplify the text above for purpose of better understanding.
            """
            # Generate summaries using Gemini
            logger.info("Calling Gemini API for summary...")
            try:
                summary_text = generate_gemini_response(
                    prompt=summary_prompt,
                    response_type="text",
                    system_prompt="You are a TEXT summarization assistant."
                )
                logger.info("Summary text generated successfully!")
            except Exception as e:
                logger.error(f"Gemini summary generation failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

            logger.info("Calling Gemini API for simplified text...")
            try:
                simplified_text = generate_gemini_response(
                    prompt=simplify_prompt,
                    response_type="text",
                    system_prompt="You are a TEXT simplification assistant."
                )
                logger.info("Simplified text generated successfully!")
            except Exception as e:
                logger.error(f"Gemini simplification failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Simplification failed: {str(e)}")

            # Create document record
            logger.info("Saving document to database...")
            try:
                db_document = Document(
                    title=file.filename,
                    type_document="video",
                    original_filename=file.filename,
                    storage_path=f"video_path:{video_path} audio_path:{audio_path}",
                    original_text=video_text,
                    uploaded_at=datetime.utcnow(),
                    user_id=user_id
                )
                db.add(db_document)
                db.commit()
                db.refresh(db_document)
                logger.info(f"Document saved with ID: {db_document.id_document}")
            except Exception as e:
                logger.error(f"Database save failed: {str(e)}")
                db.rollback()
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

            # Process text into segments
            logger.info("Creating course and segments...")
            try:
                course = create_course(db, db_document.id_document, file.filename, video_text, simplified_text, summary_text)
                process_segments(db, db_document.id_document, video_text)
                logger.info("Course and segments processed successfully!")
            except Exception as e:
                logger.error(f"Course/segment processing failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Course processing failed: {str(e)}")

            return {
                "document_id": db_document.id_document,
                "user_id": user_id,
                "course_info": {"id": course.id_course},
                "filename": file.filename,
                "storage_path": video_path,
                "audio_path": audio_path,
                "extracted_text": video_text[:100],
            }

        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")