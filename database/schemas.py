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

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
 
class UserCreate(UserBase):
    pass

class User(UserBase): 
    id : int
     
    class config: 
        # orm_mode = True # pydantic version < 2.x
        from_attribute = True # pydantic version > 2.x

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

class QuizCreate(QuizBase):
    pass  # No course_id here anymore

class Quiz(QuizBase):
    id_quiz: int
    course_id: int  # Still included in response model
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuizUserAnswerUpdate(BaseModel):
    user_answer: str

class QuizCreate(QuizBase):
    quiz_instruction: Optional[str] = None  # New optional field

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

# Update the forward references after all classes are defined
Course.model_rebuild()
Quiz.model_rebuild()