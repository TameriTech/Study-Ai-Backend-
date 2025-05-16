import os
import subprocess
from datetime import datetime
import time
import uuid
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from database.models import Document
from services.course_service import create_course
from services.segment_service import process_segments
import pytesseract
from PIL import Image
import tempfile
from utils.gemini_api import generate_gemini_response
from moviepy.editor import VideoFileClip
import whisper
# from utils.open_router import ask_openrouter  # Import the ask_openrouter function
# from utils.ollama_utils import generate_from_ollama, text_generate_from_ollama

os.makedirs("temp_files/videos", exist_ok=True)
os.makedirs("temp_files/videos/audios", exist_ok=True)
        
# ****************************ORIGINAL FIRST FUNCTION
async def extract_and_save_video(db: Session, file: UploadFile, user_id: int) -> dict:
    # First check file size before processing
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes
    
    # Get file size by seeking to end and getting position
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset file pointer to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File is too large. Maximum allowed size is 20MB."
        )

    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            allowed_extensions = ('.mp4', '.mov', '.avi', '.mkv')
            if not file.filename.lower().endswith(allowed_extensions):
                raise HTTPException(400, f"Only {', '.join(allowed_extensions)} files are allowed")

            # Save video
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
            audio_filename = f"{timestamp}_audio.mp3"  # This is the timestamped filename we want to use
            
            # Define paths in our project directory
            video_path = os.path.normpath(f"temp_files/videos/{video_filename}")
            audio_path = os.path.normpath(f"temp_files/videos/audios/{audio_filename}")  # Fixed path with slash
            
            # Write the uploaded file to disk
            with open(video_path, "wb") as buffer:
                buffer.write(await file.read())

            # Process video with MoviePy
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path, codec='mp3')
            video.close()  # Important to release resources

            # Step 3: Transcribe Audio to Text
            print("Transcribing audio... (This may take a few minutes)")
            whisper_model = whisper.load_model("base")  # Use "small", "medium", or "large" for better accuracy
            transcription = whisper_model.transcribe(audio_path)
            video_text = transcription["text"]
            print(f"Transcript extracted successfully!")  # Fixed f-string

            # Generate prompts
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
            summary_text = generate_gemini_response(
                prompt=summary_prompt,
                response_type="text",
                system_prompt="You are a TEXT summarization assistant."
            )
            print("summary text successfully!")
            simplified_text = generate_gemini_response(
                prompt=simplify_prompt,
                response_type="text",
                system_prompt="You are a TEXT simplification assistant."
            )
            print("Simplified text successfully!")
            
            # Create document record in database
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

            # Process text into segments with embeddings
            course = create_course(db, db_document.id_document, file.filename, 
                                 video_text, simplified_text, summary_text)
            process_segments(db, db_document.id_document, video_text)

            return {
                "document_id": db_document.id_document,
                "user_id": user_id,
                "course_info": {"id": course.id_course},
                "filename": file.filename,
                "storage_path": video_path,
                "audio_path": audio_path,  # Added audio path to response
                "extracted_text": video_text[:100],
            }

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=200, detail=f"Video processing failed: {str(e)}")



# *****************************************REJECT >20MB AND COMPRESS ANYTHING ABOVE 10MB      
# async def extract_and_save_video(db: Session, file: UploadFile, user_id: int) -> dict:
#     # Create a temporary directory for processing
#     with tempfile.TemporaryDirectory() as temp_dir:
#         try:
#             allowed_extensions = ('.mp4', '.mov', '.avi', '.mkv')
#             if not file.filename.lower().endswith(allowed_extensions):
#                 raise HTTPException(400, f"Only {', '.join(allowed_extensions)} files are allowed")

#             # Save video
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             video_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
#             audio_filename = f"{timestamp}_audio.mp3"
            
#             # Define paths
#             original_video_path = os.path.normpath(f"temp_files/videos/original_{video_filename}")
#             final_video_path = os.path.normpath(f"temp_files/videos/{video_filename}")
#             audio_path = os.path.normpath(f"temp_files/videos/audios/{audio_filename}")
            
#             # Write the uploaded file to disk (original)
#             with open(original_video_path, "wb") as buffer:
#                 buffer.write(await file.read())

#             # Get file size in MB
#             file_size_mb = os.path.getsize(original_video_path) / (1024 * 1024)
#             print(f"Original video size: {file_size_mb:.2f} MB")

#             # Reject files over 20MB
#             if file_size_mb > 20:
#                 os.remove(original_video_path)
#                 raise HTTPException(
#                     status_code=413,
#                     detail="File too large. Maximum allowed size is 20MB"
#                 )

#             # Compress files between 10MB-20MB to half their size
#             elif file_size_mb >= 5:
#                 print(f"Compressing video to half its size...")
#                 try:
#                     # Calculate target bitrate (roughly half the size)
#                     # Note: This is approximate as audio/video complexity affects final size
#                     target_bitrate = str(int((file_size_mb * 1024) / 2)) + "k"
                    
#                     compression_command = [
#                         'ffmpeg',
#                         '-i', original_video_path,
#                         '-vcodec', 'libx264',
#                         '-crf', '23',  # Good quality balance
#                         '-preset', 'fast',
#                         '-b:v', target_bitrate,  # Target video bitrate
#                         '-maxrate', target_bitrate,
#                         '-bufsize', '1M',  # Rate control buffer
#                         '-acodec', 'aac',
#                         '-b:a', '96k',  # Slightly reduced audio quality
#                         final_video_path
#                     ]
                    
#                     subprocess.run(compression_command, check=True, 
#                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
#                     compressed_size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
#                     print(f"Compressed video size: {compressed_size_mb:.2f} MB")
                    
#                 except subprocess.CalledProcessError as e:
#                     print(f"Compression failed, using original file: {e}")
#                     final_video_path = original_video_path  # Fallback to original
#             else:
#                 print("Video is under 10MB, skipping compression")
#                 final_video_path = original_video_path

#             # Rest of your processing logic...
#             try:
#                 video = VideoFileClip(final_video_path)
#                 video.audio.write_audiofile(audio_path, codec='mp3')
#                 video.close()

#                  # Transcribe Audio to Text
#                 print("Transcribing audio... (This may take a few minutes)")
#                 whisper_model = whisper.load_model("base")
#                 transcription = whisper_model.transcribe(audio_path)
#                 video_text = transcription["text"]
#                 print("Transcript extracted successfully!", video_text)

#                 # Generate prompts
#                 summary_prompt = f"""
#                 Here is a text extracted from a video:
#                 ---
#                 {video_text}
#                 ---
#                 Summarize the text above for revision purpose.
#                 """
                
#                 simplify_prompt = f"""
#                 Here is a text extracted from a video:
#                 ---
#                 {video_text}
#                 ---
#                 Simplify the text above for purpose of better understanding.
#                 """

#                 # Generate summaries using Gemini
#                 summary_text = generate_gemini_response(
#                     prompt=summary_prompt,
#                     response_type="text",
#                     system_prompt="You are a TEXT summarization assistant."
#                 )
#                 print("Summary text generated successfully!")
#                 simplified_text = generate_gemini_response(
#                     prompt=simplify_prompt,
#                     response_type="text",
#                     system_prompt="You are a TEXT simplification assistant."
#                 )
#                 print("Simplified text generated successfully!")
                
#                 # Create document record in database
#                 db_document = Document(
#                     title=file.filename,
#                     type_document="video",
#                     original_filename=file.filename,
#                     storage_path=f"video_path:{final_video_path} audio_path:{audio_path}",
#                     original_text=video_text,
#                     uploaded_at=datetime.utcnow(),
#                     user_id=user_id
#                 )
#                 db.add(db_document)
#                 db.commit()
#                 db.refresh(db_document)

#                 # Process text into segments with embeddings
#                 course = create_course(db, db_document.id_document, file.filename, 
#                                     video_text, simplified_text, summary_text)
#                 process_segments(db, db_document.id_document, video_text)

#                 return {
#                     "message": "Video processed successfully",
#                     "original_size": f"{file_size_mb:.2f}MB",
#                     "processed_size": f"{os.path.getsize(final_video_path) / (1024 * 1024):.2f}MB",
#                     "document_id": db_document.id_document,
#                     "user_id": user_id,
#                     "course_info": {"id": course.id_course},
#                     "filename": file.filename,
#                     "storage_path": final_video_path,
#                     "audio_path": audio_path,
#                     "extracted_text": video_text[:100],
#                 }

#             except Exception as processing_error:
#                 db.rollback()
#                 raise HTTPException(
#                     status_code=200, 
#                     detail=f"Video processing failed: {str(processing_error)}"
#                 )

#         except HTTPException:
#             # Re-raise HTTP exceptions
#             raise
#         except Exception as e:
#             raise HTTPException(
#                 status_code=200, 
#                 detail=f"Initial video handling failed: {str(e)}"
#             )
        
# ********************************************COMPRESS WHEN IT EXCEEDS 20MB
# async def extract_and_save_video(db: Session, file: UploadFile, user_id: int, compress_threshold_mb: int = 20) -> dict:
#     # Create a temporary directory for processing
#     with tempfile.TemporaryDirectory() as temp_dir:
#         try:
#             allowed_extensions = ('.mp4', '.mov', '.avi', '.mkv')
#             if not file.filename.lower().endswith(allowed_extensions):
#                 raise HTTPException(400, f"Only {', '.join(allowed_extensions)} files are allowed")

#             # Save video
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             video_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
#             audio_filename = f"{timestamp}_audio.mp3"
            
#             # Define paths
#             original_video_path = os.path.normpath(f"temp_files/videos/original_{video_filename}")
#             final_video_path = os.path.normpath(f"temp_files/videos/{video_filename}")
#             audio_path = os.path.normpath(f"temp_files/videos/audios/{audio_filename}")
            
#             # Write the uploaded file to disk (original)
#             with open(original_video_path, "wb") as buffer:
#                 buffer.write(await file.read())

#             # Get file size in MB
#             file_size_mb = os.path.getsize(original_video_path) / (1024 * 1024)
#             print(f"Original video size: {file_size_mb:.2f} MB")

#             # Only compress if file is larger than threshold
#             if file_size_mb > compress_threshold_mb:
#                 print(f"Video exceeds {compress_threshold_mb}MB, compressing...")
#                 try:
#                     # Dynamic compression based on file size
#                     crf = 28  # Default CRF for large files
#                     if file_size_mb > 100:  # Extra compression for very large files
#                         crf = 32
#                     elif file_size_mb < 70:  # Less compression for moderately large files
#                         crf = 25

#                     compression_command = [
#                         'ffmpeg',
#                         '-i', original_video_path,
#                         '-vcodec', 'libx264',
#                         '-crf', str(crf),
#                         '-preset', 'fast',
#                         '-acodec', 'aac',
#                         '-b:a', '128k',
#                         final_video_path
#                     ]
                    
#                     subprocess.run(compression_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#                     compressed_size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
#                     print(f"Compressed video size: {compressed_size_mb:.2f} MB (CRF: {crf})")
#                 except subprocess.CalledProcessError as e:
#                     print(f"Compression failed, using original file: {e}")
#                     final_video_path = original_video_path  # Fallback to original
#             else:
#                 print("Video is small enough, skipping compression")
#                 final_video_path = original_video_path

#             try:
#                 # Process video with MoviePy
#                 video = VideoFileClip(final_video_path)
#                 video.audio.write_audiofile(audio_path, codec='mp3')
#                 video.close()

        #         # Transcribe Audio to Text
        #         print("Transcribing audio... (This may take a few minutes)")
        #         whisper_model = whisper.load_model("base")
        #         transcription = whisper_model.transcribe(audio_path)
        #         video_text = transcription["text"]
        #         print("Transcript extracted successfully!")

        #         # Generate prompts
        #         summary_prompt = f"""
        #         Here is a text extracted from a video:
        #         ---
        #         {video_text}
        #         ---
        #         Summarize the text above for revision purpose.
        #         """
                
        #         simplify_prompt = f"""
        #         Here is a text extracted from a video:
        #         ---
        #         {video_text}
        #         ---
        #         Simplify the text above for purpose of better understanding.
        #         """

        #         # Generate summaries using Gemini
        #         summary_text = generate_gemini_response(
        #             prompt=summary_prompt,
        #             response_type="text",
        #             system_prompt="You are a TEXT summarization assistant."
        #         )
        #         print("Summary text generated successfully!")
        #         simplified_text = generate_gemini_response(
        #             prompt=simplify_prompt,
        #             response_type="text",
        #             system_prompt="You are a TEXT simplification assistant."
        #         )
        #         print("Simplified text generated successfully!")
                
        #         # Create document record in database
        #         db_document = Document(
        #             title=file.filename,
        #             type_document="video",
        #             original_filename=file.filename,
        #             storage_path=f"video_path:{final_video_path} audio_path:{audio_path}",
        #             original_text=video_text,
        #             uploaded_at=datetime.utcnow(),
        #             user_id=user_id
        #         )
        #         db.add(db_document)
        #         db.commit()
        #         db.refresh(db_document)

        #         # Process text into segments with embeddings
        #         course = create_course(db, db_document.id_document, file.filename, 
        #                             video_text, simplified_text, summary_text)
        #         process_segments(db, db_document.id_document, video_text)

        #         return {
        #             "document_id": db_document.id_document,
        #             "user_id": user_id,
        #             "course_info": {"id": course.id_course},
        #             "filename": file.filename,
        #             "storage_path": final_video_path,
        #             "audio_path": audio_path,
        #             "extracted_text": video_text[:100],
        #         }

        #     except Exception as processing_error:
        #         db.rollback()
        #         raise HTTPException(
        #             status_code=200, 
        #             detail=f"Video processing failed: {str(processing_error)}"
        #         )

        # except HTTPException:
        #     # Re-raise HTTP exceptions
        #     raise
        # except Exception as e:
        #     raise HTTPException(
        #         status_code=200, 
        #         detail=f"Initial video handling failed: {str(e)}"
        #     )