from fastapi import UploadFile, HTTPException
import fitz  # PyMuPDF
from utils.ollama_utils import generate_from_ollama
from fastapi import UploadFile, HTTPException
import fitz  # PyMuPDF


async def extract_pdf_text(file: UploadFile):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    contents = await file.read()
    with open("temp.pdf", "wb") as f:
        f.write(contents)

    text = ""
    with fitz.open("temp.pdf") as pdf:
        for page in pdf:
            text += page.get_text()

    return {
        "filename": file.filename,
        "extracted_text": text
    }


async def summarize_pdf(file: UploadFile):
    text = await extract_pdf_text(file)

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


async def generate_mcqs_from_pdf(file: UploadFile):
    text = await extract_pdf_text(file)

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
