from database.db import Base
from sqlalchemy import Boolean, Integer, Column, String, Date, Numeric
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import numpy as np
import json

# Enum for document types
class DocumentTypeEnum(str, enum.Enum):
    pdf = "pdf"
    image = "image"
    video = "video"

# Enum for quiz types
class QuizEnumType(str, enum.Enum):
    mcq = "mcq"
    text = "text"
    true_or_false = "true_or_false"

class QuizDifficultyLevelEnum(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    fullName = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    best_subjects = Column(String)
    learning_objectives = Column(String)
    class_level = Column(String)
    academic_level = Column(String)
    statistic = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="user")

class Document(Base):
    __tablename__ = "Documents"

    id_document = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type_document = Column(String)
    original_filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    original_text = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    segments = relationship("Segment", back_populates="document")
    courses = relationship("Course", back_populates="document")

class Course(Base):
    __tablename__ = "Courses"
    
    id_course = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(255), nullable=False)
    original_text = Column(String)
    simplified_text = Column(String)
    summary_text = Column(String)
    level_of_difficulty = Column(Enum(QuizDifficultyLevelEnum), nullable=True)
    estimated_completion_time = Column(String(50))
    quiz_instruction = Column(String, nullable=True)
    summary_modules = Column(JSON)
    simplified_modules = Column(JSON)

    simplified_module_pages = Column(Integer, default=0)
    simplified_current_page = Column(Integer, default=1)
    
    summary_current_page = Column(Integer, default=1)
    summary_module_pages = Column(Integer, default=0)

    simplified_module_statistic = Column(Numeric(10, 2), default=0)  # 10 digits total, 2 after decimal
    summary_modules_statistic = Column(Numeric(10, 2), default=0)
    
    has_quiz = Column(Boolean, default=False, nullable=False)
    document_id = Column(Integer, ForeignKey('Documents.id_document'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="courses")
    quizzes = relationship("Quiz", back_populates="course")
    vocabularies = relationship("Vocabulary", back_populates="course")
    feedbacks = relationship("Feedback", back_populates="course")


class Segment(Base):
    __tablename__ = "Segments"

    id_segment = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('Documents.id_document'), nullable=False)
    raw_text = Column(String, nullable=False)
    embedding_vector = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="segments")

    def set_embedding(self, vector: np.ndarray):
        """Serialize numpy array to JSON string for storage"""
        self.embedding_vector = json.dumps(vector.tolist())
    
    def get_embedding(self) -> np.ndarray:
        """Deserialize JSON string back to numpy array"""
        return np.array(json.loads(self.embedding_vector)) if self.embedding_vector else None

class Quiz(Base):
    __tablename__ = "Quizzes"

    id_quiz = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey('Courses.id_course'), nullable=False)
    question = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    user_answer = Column(String, nullable=True)  # Initially nullable until user answers
    choices = Column(JSON, nullable=False)
    quiz_type = Column(Enum(QuizEnumType), nullable=False)
    level_of_difficulty = Column(Enum(QuizDifficultyLevelEnum), nullable=False)
    number_of_questions = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="quizzes")

class Vocabulary(Base):
    __tablename__ = "Vocabularies"

    id_term = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey('Courses.id_course'), nullable=False)
    words = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="vocabularies")

class Feedback(Base):
    __tablename__ = "Feedbacks"

    id_feedback = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey('Courses.id_course'), nullable=False)  # updated from quiz_id
    rating = Column(Integer, nullable=False)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="feedbacks")

class Comment(Base):
    __tablename__ = "Comments"

    id_comment = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)  # User who made the comment
    quiz_id = Column(Integer, ForeignKey('Quizzes.id_quiz'), nullable=True)  # Optional, if related to a quiz
    course_id = Column(Integer, ForeignKey('Courses.id_course'), nullable=True)  # Optional, if related to a course
    comment_text = Column(String, nullable=False)  # Text of the comment
    likes = Column(Integer, default=0)  # Number of likes
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="comments")  # Relationship to User
    quiz = relationship("Quiz", backref="comments")  # Relationship to Quiz (optional)
    course = relationship("Course", backref="comments")  # Relationship to Course (optional)
    
    def __repr__(self):
        return f"<Comment(user_id={self.user_id}, quiz_id={self.quiz_id}, course_id={self.course_id}, likes={self.likes})>"
