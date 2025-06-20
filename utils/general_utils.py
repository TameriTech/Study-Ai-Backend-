from datetime import datetime, timedelta
import io
import json
import re
from typing import Dict, List
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF
from datetime import datetime
from sqlalchemy.orm import Session
from PIL import Image
from fastapi import UploadFile, HTTPException
from PIL import Image

# Load environment variables from .env file
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


import re
import json

def extract_and_parse_questions(response):
    """
    Extracts and parses the 'Questions' JSON array from the model's response content.
    Accepts either a raw string or full OpenRouter response object.
    """
    # Step 1: Handle full response object (dict)
    if isinstance(response, dict):
        try:
            response = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise ValueError("Invalid model response format")

    # Step 2: Ensure response is a string
    if not isinstance(response, str):
        raise TypeError("Expected response to be a string")

    # Step 3: Try direct JSON load if response is pure JSON
    try:
        full_data = json.loads(response)
        if isinstance(full_data, dict) and "Questions" in full_data:
            return full_data["Questions"]
    except json.JSONDecodeError:
        pass  # Fallback to regex parsing

    # Step 4: Use regex to extract just the array if needed
    match = re.search(r'\[\s*{.*?}\s*]', response, re.DOTALL)
    if not match:
        raise ValueError("No JSON array found between square brackets")

    json_str = match.group(0)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in extracted array: {e}")


def parse_modules(module_text: str) -> List[Dict[str, str]]:
    modules = []
    # Split by module headers
    module_sections = re.split(r'Module \d+: ', module_text)[1:]  # Skip first empty
    
    for section in module_sections:
        if not section.strip():
            continue
            
        # Extract module title (first line)
        lines = section.split('\n')
        module_title = lines[0].strip()
        
        # Initialize module structure
        module = {
            'title': module_title,
            'topics': []
        }
        
        # Process each topic
        current_topic = None
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('* Topic:'):
                if current_topic:  # Save previous topic if exists
                    module['topics'].append(current_topic)
                current_topic = {
                    'name': line.replace('* Topic:', '').strip(),
                    'body': ''
                }
            elif line.startswith('* Body:') and current_topic:
                current_topic['body'] = line.replace('* Body:', '').strip()
            elif current_topic:  # Continuation of body
                current_topic['body'] += ' ' + line.strip()
        
        # Add the last topic if exists
        if current_topic:
            module['topics'].append(current_topic)
        modules.append(module)
    
    return modules

def parse_vocabulary_response(response_text: str) -> List[Dict[str, str]]:
    """
    Extract and parse the first JSON array found between square brackets []
    """
    # Find the first occurrence of content between []
    match = re.search(r'\[.*\]', response_text, re.DOTALL)
    if not match:
        raise ValueError("No vocabulary array found in response")
    
    try:
        # Parse the matched JSON array
        vocabulary_list = json.loads(match.group(0))
        
        # Validate it's a list of dictionaries with required fields
        if not isinstance(vocabulary_list, list):
            raise ValueError("Expected an array of vocabulary terms")
            
        for term in vocabulary_list:
            if not isinstance(term, dict) or 'term' not in term or 'definition' not in term:
                raise ValueError("Each vocabulary item must have 'term' and 'definition' keys")
                
        return vocabulary_list
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")


# Password hashing (already added, repeating for context)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Token creation
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Token verification
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

# To verify if user is auth to use it to set restriction
def get_current_user(token: str = Depends(oauth2_scheme)):
    user_email = decode_access_token(token)
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_email

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