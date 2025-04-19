from fastapi import UploadFile, HTTPException
from PIL import Image
import pytesseract
import io
from utils.ollama_utils import generate_from_ollama

async def extract_text_from_image(file: UploadFile):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    contents = await file.read()

    try:
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing error: {str(e)}")

    return {
        "filename": file.filename,
        "extracted_text": text.strip()
    }

async def summarize_image_text(file: UploadFile):
    text = await extract_text_from_image(file)

    prompt = f"""
    Here is a text from a PDF document:

    ---
    {text}
    ---

    Summarize the text above for revision purpose.
    """

    summary = generate_from_ollama(prompt)

    return {
        "filename": file.filename,
        "summary": summary
    }


async def generate_mcqs_from_image_text(file: UploadFile):
    text = await extract_text_from_image(file)

    prompt = f"""
    Based on the following text from a PDF document:

    ---
    {text}
    ---

    Create 10 multiple-choice questions (MCQs). Each question should have:
    - 4 answer options labeled A, B, C, and D.
    - Clearly indicate which option is correct (e.g., "Correct Answer: B").

    Return the questions in a numbered list.
    """

    mcqs = generate_from_ollama(prompt)

    return {
        "filename": file.filename,
        "mcqs": mcqs
    }
