from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from database.models import Document
from database.schemas import DocumentCreate
import os

class DocumentService:
    def create_document(self, db: Session, document_data: dict, file_content: str, user_id: int):
        """
        Creates a new document and saves it to the database
        """
        db_document = Document(
            user_id=user_id,
            title=document_data.get("title", os.path.splitext(document_data["original_filename"])[0]),
            type_document=document_data.get("type_document"),
            original_filename=document_data["original_filename"],
            storage_path=document_data["storage_path"],
            original_text=file_content,
            uploaded_at=datetime.utcnow()
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    
    def get_document(self, db: Session, document_id: int):
        return db.query(Document).filter(Document.id_document == document_id).first()
    
    def get_documents(
        self,
        db: Session,
        title_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ):
        query = db.query(Document)
        
        if title_filter:
            query = query.filter(Document.title.ilike(f"%{title_filter}%"))
        if type_filter:
            query = query.filter(Document.type_document == type_filter)
        
        return query.offset(skip).limit(limit).all()
document_service = DocumentService()