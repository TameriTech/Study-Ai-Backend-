from pydantic import BaseModel
from datetime import date

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

