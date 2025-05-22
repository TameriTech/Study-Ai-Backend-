from pydantic import BaseModel, Field
from datetime import date
from datetime import datetime
from typing import Dict, Optional, List, Any
from enum import Enum

# Enums (already defined in SQLAlchemy, repeating here for Pydantic)
class DocumentTypeEnum(str, Enum):
    pdf = "pdf"
    image = "image"
    video = "video"

class QuizEnumType(str, Enum):
    mcq = "mcq"
    text = "text"
    true_or_false = "true_or_false"

class QuizDifficultyLevelEnum(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class UserBase(BaseModel):
    fullName: str
    email: str
    class_level: str
    password: str
    best_subjects: str
    learning_objectives: str
    academic_level: str
    statistic: int
    # dateOfBirth: date
 
class UserUpdate(BaseModel):
    fullName: Optional[str] = None
    email: Optional[str] = None
    class_level: Optional[str] = None
    best_subjects: Optional[str] = None
    learning_objectives: Optional[str] = None
    academic_level: Optional[str] = None
    statistic: Optional[int] = None

# In your schemas.py
class PasswordResetRequest(BaseModel):
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase): 
    id : int
     
    class config: 
        orm_mode = True # pydantic version < 2.x
        # from_attribute = True # pydantic version > 2.x

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class GoogleToken(BaseModel):
    id_token: str

class FacebookToken(BaseModel):
    access_token: str

class SocialLoginResponse(TokenResponse):
    provider: str = Field(..., description="Authentication provider (google or facebook)")

# Course related schemas
class CourseBase(BaseModel):
    course_name: str
    original_text: Optional[str] = None
    simplified_text: Optional[str] = None
    summary_text: Optional[str] = None
    level_of_difficulty: QuizDifficultyLevelEnum
    quiz_instruction: str
    estimated_completion_time: Optional[str] = None
    summary_modules: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    simplified_modules: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    simplified_module_pages: Optional[int] = 0
    summary_module_pages: Optional[int] = 0
    summary_current_page: Optional[int] = 1
    simplified_current_page: Optional[int] = 1 
    simplified_module_statistic: Optional[float] = 0.0  # Changed to float since it was Float in SQLAlchemy
    summary_modules_statistic: Optional[float] = 0.0  # Changed to float
    document_id: int

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id_course: int
    created_at: datetime
    quizzes: List['Quiz'] = []
    vocabularies: List['Vocabulary'] = []
    
    class Config:
        from_attributes = True

class CourseSearchResult(Course):
    pass  # Inherits all fields from Course

class CourseSearchResponse(BaseModel):
    results: List[CourseSearchResult]
    pagination: dict = Field(
        example={
            "total": 15,
            "returned": 10,
            "skip": 0,
            "limit": 10
        }
    )

class QuizBase(BaseModel):
    course_id: int
    question: str
    correct_answer: str
    user_answer: str
    choices: Dict[Any, Any]
    quiz_type: QuizEnumType  # Now uses correct enum
    level_of_difficulty: QuizDifficultyLevelEnum  # Separate enum for difficulty
    number_of_questions: int
    course_name: Optional[str] = None  # Add this line

class Quiz(QuizBase):
    id_quiz: int
    course_id: int  # Still included in response model
    course_name: str  # Add this field
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuizUserAnswerUpdate(BaseModel):
    user_answer: str

class QuizCreateRequest(BaseModel):
    """Schema for quiz creation request (what the client sends)"""
    course_id: int
    quiz_type: QuizEnumType
    level_of_difficulty: QuizDifficultyLevelEnum
    number_of_questions: int
    quiz_instruction: Optional[str] = None

class QuizCreate(QuizBase):
    pass  # No course_id here anymore

# Vocabulary related schemas
class VocabularyBase(BaseModel):
    course_id: int
    words: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class VocabularyCreate(VocabularyBase):
    pass

class Vocabulary(VocabularyBase):
    id_term: int
    created_at: datetime
    
    class Config:
        from_attributes = True
        
class VocabularyWords(BaseModel):
    words: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class VocabularyCreate(BaseModel):
    course_id: int = Field(..., example=1)
    words: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class VocabularySearchResult(BaseModel):
    term: str
    definition: str
    
class VocabularySearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    pagination: Dict[str, int] = Field(
        example={"total": 15, "returned": 10, "skip": 0}
    )

# Feedback related schemas
class FeedbackBase(BaseModel):
    course_id: int
    rating: int
    comment: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id_feedback: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Comment related schemas
class CommentBase(BaseModel):
    user_id: int  # User who made the comment
    course_id: Optional[int] = None  # Optional: related to a course
    comment_text: str  # Text of the comment
    likes: int = Field(default=0, ge=0, le=5, description="Number of likes, range 0-5") 

class CommentCreate(CommentBase):
    pass  # You can extend this if there are additional fields for creating comments

class Comment(CommentBase):
    id_comment: int  # The primary key for the comment
    created_at: datetime  # Timestamp when the comment was created

    class Config:
        from_attributes = True  # Enable Pydantic to support ORM mode

class CommentSearchResponse(BaseModel):
    results: List[Comment]  # List of comments in the response
    pagination: dict = Field(
        example={
            "total": 15,
            "returned": 10,
            "skip": 0,
            "limit": 10
        }
    )

class QuestionRequest(BaseModel):
    """Schema for asking questions to the chatbot"""
    question: str = Field(..., description="The question to ask the chatbot")
    document_id: Optional[int] = Field(
        None,
        description="Optional document ID to restrict the search to a specific document"
    )

class AnswerResponse(BaseModel):
    """Schema for the chatbot's response"""
    answer: str = Field(..., description="The generated answer to the question")
    sources: List[int] = Field(
        default_factory=list,
        description="List of segment IDs used to generate the answer"
    )
    relevant_segments: List[str] = Field(
        default_factory=list,
        description="The actual text of the relevant segments used"
    )
    confidence: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Confidence score of the answer (0-1)"
    )

    class Config:
        from_attributes = True
class DocumentBase(BaseModel):
    title: str
    type_document: Optional[str] = None
    original_filename: str

class DocumentCreate(DocumentBase):
    storage_path: str
    original_text: Optional[str] = None

class Document(DocumentBase):
    id_document: int
    user_id: int
    storage_path: str
    original_text: Optional[str] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True  # Replaces orm_mode = True in Pydantic v2

# Segment Schemas
class SegmentBase(BaseModel):
    raw_text: str
    
class SegmentCreate(SegmentBase):
    document_id: int

class Segment(SegmentBase):
    id_segment: int
    document_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat Schemas
class QuestionRequest(BaseModel):
    question: str
    document_id: Optional[int] = None

class AnswerResponse(BaseModel):
    answer: str
    sources: List[int]
    relevant_segments: List[str]
# Update the forward references after all classes are defined
Course.model_rebuild()
Quiz.model_rebuild()