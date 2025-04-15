from pydantic import BaseModel


class PDFUpload(BaseModel):
    filename: str
    content_base64: str 