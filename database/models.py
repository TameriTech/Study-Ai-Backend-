from database.db import Base
from sqlalchemy import Integer, Column, String, Date
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Enum for document types
class DocumentTypeEnum(str, enum.Enum):
    pdf = "pdf"
    video = "video"

# Enum for quiz types
class QuizTypeEnum(str, enum.Enum):
    qcm = "qcm"
    texte = "texte"

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    fullName = Column(String, index=True)
    email = Column(String, unique=True, index=True)  # Make email unique
    password = Column(String, index=True)  # Store hashed password
    # dateOfBirth = Column(Date, index=True) Use Date type
    best_subjects = Column(String, index=True)
    learning_objectives = Column(String, index=True)
    class_level = Column(String, index=True)
    academic_level = Column(String, index=True)
    statistic = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "document"

    id_document = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type_document = Column(Enum(DocumentTypeEnum), nullable=False)
    original_filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    segments = relationship("Segment", back_populates="document")

class Segment(Base):
    __tablename__ = "segment"

    id_segment = Column(Integer, primary_key=True, index=True)
    id_document = Column(Integer, ForeignKey("document.id_document"), nullable=False)
    raw_text = Column(String, nullable=False)
    summary_text = Column(String)
    simplified_text = Column(String)
    embedding_vector = Column(String)  # Adjust type if using specific vector types
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="segments")
    quizzes = relationship("Quiz", back_populates="segment")
    vocabularies = relationship("Vocabulary", back_populates="segment")

class Quiz(Base):
    __tablename__ = "quiz"

    id_quiz = Column(Integer, primary_key=True, index=True)
    id_segment = Column(Integer, ForeignKey("segment.id_segment"), nullable=False)
    instruction = Column(String, nullable=False)
    question = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    choices = Column(JSON, nullable=False)  # Ensure your database supports JSON
    quiz_type = Column(Enum(QuizTypeEnum), nullable=False)
    level_of_difficulty = Column(Enum(QuizTypeEnum), nullable=False)
    number_of_questions = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    segment = relationship("Segment", back_populates="quizzes")
    feedbacks = relationship("Feedback", back_populates="quiz")

class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id_term = Column(Integer, primary_key=True, index=True)
    id_segment = Column(Integer, ForeignKey("segment.id_segment"), nullable=False)
    term = Column(String, nullable=False)
    definition = Column(String, nullable=False)

    segment = relationship("Segment", back_populates="vocabularies")

class Feedback(Base):
    __tablename__ = "feedback"

    id_feedback = Column(Integer, primary_key=True, index=True)
    id_quiz = Column(Integer, ForeignKey("quiz.id_quiz"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    quiz = relationship("Quiz", back_populates="feedbacks")