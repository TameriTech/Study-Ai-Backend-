from fastapi import APIRouter
from app.schemas.pdf_schema import PDFUpload
from app.services.pdf_service import process_pdf


router = APIRouter()

@router.post("/upload-pdf")
def upload_pdf(pdf: PDFUpload):
    """
    Upload a PDF file and process it.
    """
    try:
        # Call the service to process the PDF
        result =  process_pdf(pdf.file_name, pdf.content)
        return {"message": "PDF processed successfully", "result": result}
    except Exception as e:
        return {"error": str(e)}