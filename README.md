# 📚 Study AI – Plateforme d'apprentissage intelligente

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Status](https://img.shields.io/badge/status-en%20cours-yellow)

---

## 📑 Table des matières

- [Présentation](#-study-ai--plateforme-dapprentissage-intelligente)
- [Objectifs](#-objectifs)
- [Fonctionnalités](#-fonctionnalités-principales)
- [Technologies](#-technologies-utilisées)
- [Architecture](#-architecture-du-projet)
- [Structure](#-structure-du-projet-studyai)
- [Contraintes](#-contraintes--défis)
- [Critères de validation](#-critères-de-validation)
- [Tests](#-tests)
- [Installation & Lancement](#-lancement-rapide-dev)
- [Fichier .env](#-exemple-de-fichier-env)
- [Contribution](#-contribuer)
- [Contact](#-auteurs--contribution)

---

## 🧠 Présentation

**Study AI** est une application innovante développée par **Tameri Tech** pour transformer l'apprentissage des étudiants. Elle permet d'automatiser l'analyse de contenus pédagogiques (PDF, vidéos) grâce à l'intelligence artificielle, et génère des fiches de révision et des quiz personnalisés.

---

## 🚀 Objectifs

- Offrir une solution interactive pour réviser efficacement
- Générer automatiquement des contenus à partir de documents/vidéos
- Améliorer la pertinence via l'IA et les retours utilisateurs

---

## 🧩 Fonctionnalités principales

- 📄 **PDF** : Importation, extraction, analyse de contenu
- 🎥 **Vidéos** : Traitement image, reconnaissance vocale
- 🖋️ **Génération automatique** : Fiches de révision, quiz personnalisés
- 🤖 **IA & Feedback** : Amélioration continue, retours utilisateurs
- 📊 **Dashboard interactif** : Accès aux fichiers, fiches et statistiques

---

## 🛠️ Technologies utilisées

| Composant       | Technologies                                                  |
|----------------|---------------------------------------------------------------|
| Backend         | Python, FastAPI                                               |
| Frontend        | Kotlin (Java) *(optionnel)*                                   |
| Base de données | PostgreSQL                                                    |
| PDF             | PDFMiner, Apache Tika                                         |
| Vidéo & Audio   | OpenCV, Google/Azure Speech-to-Text                           |
| IA              | OpenAI API (GPT-4), TensorFlow / PyTorch                      |

---

## 📊 Architecture du projet

L'application suit une **architecture modulaire en couches** :

- Routes FastAPI (pdf, vidéos, quiz, feedback, user)
- Services de traitement (OCR, NLP, IA, audio)
- Moteur de génération de quiz & fiches
- Système de feedback
- Base de données et modèles ORM

---

## 📁 Structure du projet StudyAI

```bash

Study-Ai-Backend/
│
├── api/                          # Contains all route/controller logic
│   ├── courses.py
│   ├── documents.py
│   ├── feedback.py
│   ├── quiz.py
│   ├── segments.py
│   ├── users.py
│   └── vocabulary.py
│
├── database/                     # Database layer: connection, models, and schemas
│   ├── db.py
│   ├── models.py
│   └── schemas.py
│
├── services/                     # Business logic and service layer
│   ├── course_service.py
│   ├── document_service.py
│   ├── feedback_service.py
│   ├── quiz_service.py
│   ├── segment_service.py
│   ├── users_services.py
│   └── vocabulary_services.py
│
├── utils/                        # Utility functions for reusability
│   ├── general_utils.py
│   ├── image_util.py
│   ├── ollama_utils.py
│   ├── pdf_util.py
│   └── video_util.py
│
├── temp_files/                   # Temporary storage for uploaded or processed files
│   ├── images/                   # Temporary image files
│   ├── pdf/                      # Temporary PDF documents
│   └── videos/                   # Temporary video files
│
├── .env                          # Environment variables
├── .gitignore                    # Git ignored files/folders
├── api_documentation.md         # API documentation
├── main.py                       # Application entry point
├── README.md                     # Project description and instructions
├── requirements.txt              # Python dependencies
└── TODO.md                       # Tasks and future enhancements
```

---

## ⚠️ Contraintes & défis

- Gestion de PDF variés (avec code, images, etc.)
- Qualité des vidéos/audio parfois faible
- Temps de traitement de gros fichiers
- Interface à la fois intuitive et riche

---

## ✅ Critères de validation

| Fonctionnalité       | Critère attendu                                     |
|----------------------|------------------------------------------------------|
| PDF                  | Précision > 95%                                     |
| Vidéo               | Concepts extraits dans > 90% des cas                 |
| Quiz                 | Pertinence du contenu généré                       |
| Performance          | Temps de réponse acceptable (même fichiers lourds)   |
| Feedback utilisateur | Système intuitif, utilisé activement                |

---

## 🧪 Tests

- 🔬 **Unitaires** : PDFImporter, VideoAnalyzer, QuizGenerator
- 🔗 **Intégration** : Chaîne complète (import → quiz)
- 🔍 **Fonctionnels** : Cas d’usage réels
- 📊 **Performance** : Scalabilité, charge
- 👥 **Utilisateurs** : Feedback humain pour ajustement

---

## 🏁 Lancement rapide (dev)

```bash
# Cloner le projet
git clone https://github.com/TameriTech/Study-Ai-Backend-.git
cd study-ai

# Créer l'environnement virtuel
python -m venv env
source env/Scripts/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
uvicorn app.main:app --reload
```

---

## 🔐 Exemple de fichier `.env`

```env
OPENAI_API_KEY=sk-xxx
GOOGLE_SPEECH_API_KEY=xxx
DATABASE_URL=postgresql://user:password@localhost/studyai
```

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

- Forkez le repo
- Créez une branche (`git checkout -b feature/ma-feature`)
- Commitez vos changements
- Push (`git push origin feature/ma-feature`)
- Ouvrez une pull request 🚀

---

## 📢 Auteurs & Contribution

**Développé par :** Tameri Tech  
**Contact :** [tameri.tech25@gmail.com](mailto:tameri.tech25@gmail.com)

> Diagrammes UML disponibles dans le rapport d’analyse officiel du projet.

---

**✨ Rejoignez la révolution de l'apprentissage intelligent avec Study AI.**

===========================================================================

![studyAI_DB](https://github.com/user-attachments/assets/891edbc1-22ce-4f69-90e0-437a14dce81c)
![q](https://github.com/user-attachments/assets/418391b4-52a6-49ca-b36f-1fa03057cd79)

===========================================================================

Here's a clear and professional documentation for the `users_services` module based on your provided code. This can be added to your `api_documentation.md` or kept separately under a **Services Documentation** section.

---

## 🧩 `users_services.py` – User Service Logic

This module handles **CRUD operations** and **authentication logic** for users.

### 🔒 Authentication

```python
def authenticate_user(db: Session, email: str, password: str)
```

- **Purpose**: Validates user credentials.
- **Parameters**:
  - `db`: SQLAlchemy DB session.
  - `email` *(str)*: User's email address.
  - `password` *(str)*: Plain-text password to verify.
- **Returns**: User object if credentials are valid, otherwise `None`.

---

### 🧑 Create User

```python
def create_user(db: Session, data: UserCreate)
```

- **Purpose**: Creates a new user after checking for email uniqueness.
- **Parameters**:
  - `db`: SQLAlchemy DB session.
  - `data`: Pydantic schema `UserCreate` containing user details.
- **Logic**:
  - Checks if the email already exists.
  - Hashes the password before storing.
- **Raises**: `HTTPException` with status `400` if email already exists.
- **Returns**: The newly created user object.

---

### 📥 Get All Users

```python
def get_users(db: Session)
```

- **Purpose**: Fetches all users from the database.
- **Returns**: List of user objects.

---

### 👤 Get a Single User

```python
def get_user(db: Session, user_id: int)
```

- **Purpose**: Fetches a user by their ID.
- **Returns**: A single user object or `None` if not found.

---

### ✏️ Update User

```python
def update_user(db: Session, user: UserCreate, user_id: int)
```

- **Purpose**: Updates user fields with new data.
- **Parameters**:
  - `db`: SQLAlchemy DB session.
  - `user`: New user data (as `UserCreate` schema).
  - `user_id`: ID of the user to update.
- **Logic**: Dynamically updates fields using `model_dump()`.
- **Returns**: The updated user object or `None` if not found.

---

### ❌ Delete User

```python
def delete_user(db: Session, user_id: int)
```

- **Purpose**: Deletes a user by their ID.
- **Returns**: The deleted user object or `None` if not found.

---



===========================================================================

Here's the comprehensive documentation Documents module following your established style:

---

## 📄 `documents services` – Document Processing Service

Handles file uploads (PDFs, images, videos), text extraction, and initial processing pipeline including:
- File storage management
- Text extraction (OCR for images/videos)
- AI-powered summarization/simplification
- Automatic course creation
- Text segmentation with embeddings

---

### 📑 **PDF Processing**
```python
async def extract_and_save_pdf(db: Session, file: UploadFile, user_id: int) -> dict
```

#### Features
- Validates PDF files
- Extracts raw text using PyMuPDF
- Generates AI summaries and simplifications
- Creates database records and initiates processing pipeline

#### Parameters
| Parameter | Type          | Description                          |
|-----------|---------------|--------------------------------------|
| `db`      | `Session`     | SQLAlchemy database session          |
| `file`    | `UploadFile`  | PDF file to process                  |
| `user_id` | `int`         | Owner's user ID                      |

#### Returns
```json
{
  "document_id": 123,
  "user_id": 456,
  "filename": "notes.pdf",
  "storage_path": "temp_files/pdf/20240101_123456_notes.pdf",
  "extracted_text": "Lorem ipsum...",
  "message": "PDF processed successfully..."
}
```

#### Error Cases
- `400 Bad Request`: Non-PDF file uploaded
- `500 Internal Server Error`: File processing failures

---

### 📸 **Image Processing**
```python
async def extract_and_save_image(db: Session, file: UploadFile, user_id: int) -> dict
```

#### Features
- Accepts common image formats (JPEG, PNG, etc.)
- Performs OCR using Tesseract
- Parallel processing pipeline to PDF documents

#### Special Considerations
```python
# Requires Tesseract OCR installed:
# sudo apt install tesseract-ocr  # Linux
# brew install tesseract           # macOS
```

#### Error Cases
- `400 Bad Request`: Non-image file uploaded
- `500 Internal Server Error`: OCR processing failures

---

### 🎥 **Video Processing**
```python
async def extract_and_save_video(
    db: Session, 
    file: UploadFile, 
    user_id: int, 
    frames_per_second: int = 1
) -> dict
```

#### Features
- Supports MP4, MOV, AVI, MKV
- Frame extraction via FFmpeg
- Per-frame OCR processing
- Configurable FPS for performance/coverage tradeoff

#### Dependencies
```bash
# Requires FFmpeg:
# sudo apt install ffmpeg  # Linux
# brew install ffmpeg      # macOS
```

#### Error Cases
- `400 Bad Request`: Unsupported video format
- `500 Internal Server Error`: FFmpeg/OCR processing failures

---

### 🔄 **Common Processing Pipeline**
All methods follow this workflow:
1. File validation → 2. Storage → 3. Text extraction →  
4. AI processing → 5. Database records → 6. Course/Segment creation

#### Shared Return Structure
All successful operations return:
- Document metadata
- Extracted text sample
- Processing confirmation
- Generated course ID

#### Error Handling
Uniform error responses with:
- Machine-readable status codes
- Human-friendly error messages
- Contextual details for debugging

---

### 🛠 **Utility Functions**
| Function                | Description                                  |
|-------------------------|----------------------------------------------|
| `_save_to_temp()`       | Handles secure file storage with timestamped names |
| `_validate_file_type()` | Checks file extensions and MIME types        |

---



===========================================================================

Here's the comprehensive documentation for your `course_service.py` module:

---

## 📚 `course_service.py` – Course Management Service

Handles course creation, module processing, progress tracking, and search functionality for your learning platform.

---

### ➕ **Create Course**
```python
def create_course(
    db, 
    document_id: int,
    course_name: str,
    original_text: Optional[str] = None,
    simplified_text: Optional[str] = None,
    summary_text: Optional[str] = None,
    level: str = "beginner"
) -> Course
```

#### Features
- Automatically structures content into modules using AI
- Generates estimated completion time
- Creates both simplified and summary versions
- Calculates initial pagination statistics

#### AI Processing Pipeline
1. **Module Generation**:
   ```python
   simplified_modules = generate_from_ollama(prompt)  # For both simplified/summary
   ```
2. **Time Estimation**:
   ```python
   estimated_time = generate_from_ollama("...text...")  # <12 character response
   ```

#### Returns
`Course` object with:
- Structured modules (JSON)
- Pagination counts
- Original/processed content
- Completion metrics

---

### 🔍 **Module Retrieval**
| Function | Description |
|----------|-------------|
| `get_simplified_modules()` | Gets simplified modules by document ID |
| `get_summary_modules()` | Gets summary modules by document ID |
| `get_simplified_modules_by_course_id()` | Gets modules by course ID |
| `get_summary_modules_by_course_id()` | Gets summary by course ID |

**All functions return**:  
`List[Dict]` or `None` if not found

---

### 📈 **Progress Tracking**
```python
def update_simplified_progress(db, course_id, current_page) -> Course
def update_summary_progress(db, course_id, current_page) -> Course
```

#### Features
- Auto-calculates completion percentage
- Prevents page overflow
- Updates both current page and statistics

**Example**:
```python
# Updates page 3 of 10 → 30% completion
update_simplified_progress(db, 123, 3)  
```

---

### 🗂 **Course Access**
| Function | Description |
|----------|-------------|
| `get_course_from_db()` | Gets full course by ID |
| `get_user_courses()` | Lists all courses for a user |

**Returns**:  
- Single `Course` object or `None`
- List of courses (SQLAlchemy objects)

---

### 🔎 **Advanced Search**
```python
def search_courses(
    db,
    search_query: str,
    min_query_length=2,
    limit=10,
    skip=0,
    search_fields=None,
    fuzzy_match=False
) -> dict
```

#### Features
- Field-specific searching (default: course_name)
- Fuzzy matching (PG trigram similarity)
- Pagination support

**Search Options**:
```python
# Exact match on multiple fields
search_courses(db, "math", search_fields=["course_name", "original_text"])

# Fuzzy matching
search_courses(db, "algebr", fuzzy_match=True)
```

**Return Structure**:
```json
{
  "results": [Course1, Course2],
  "pagination": {
    "total": 15,
    "returned": 2,
    "skip": 0,
    "limit": 10
  }
}
```

#### Error Cases
- `400 Bad Request`: Query too short
- `400 Bad Request`: Invalid search fields

---

### 🛠 **Internal Utilities**
| Function | Description |
|----------|-------------|
| `parse_modules()` | Converts AI output to structured modules |
| `_calculate_progress()` | Handles percentage calculations |

---

===========================================================================

Here's the documentation for your `segment_service.py` module:

---

## 🔍 `segment_service.py` – Text Segmentation & Embedding Service

Handles text chunking and vector embedding generation for semantic search and content analysis.

---

### ⚙️ **Core Function**
```python
def process_segments(
    db: Session, 
    document_id: int, 
    text: str, 
    chunk_size: int = 1000
) -> int
```

#### Features
- Splits text into manageable chunks
- Generates 384-dimension embeddings using `all-MiniLM-L6-v2` model
- Stores embeddings as JSON-serialized arrays
- Skips empty/whitespace chunks
- Returns count of created segments

#### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `db` | `Session` | - | SQLAlchemy session |
| `document_id` | `int` | - | Parent document ID |
| `text` | `str` | - | Raw content to process |
| `chunk_size` | `int` | 1000 | Character length per segment |

#### Technical Details
```python
# Embedding Generation
embedding = model.encode(text_chunk)  # Returns numpy array
vector = json.dumps(embedding.tolist())  # Serialized storage

# Chunking Logic
chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
```

#### Returns
Integer count of successfully created segments

---

### 🧮 **Embedding Specifications**
| Model | Dimensions | Size | Best For |
|-------|------------|------|----------|
| `all-MiniLM-L6-v2` | 384 | ~80MB | Fast semantic search |

---

### 💾 **Database Storage**
```python
class Segment(BaseModel):
    embedding_vector: str  # JSON string of float array
    raw_text: str         # Original chunk content
    document_id: int      # Foreign key
```

#### Retrieval Example
```python
# Get embedding back to numpy array
segment = db.query(Segment).first()
embedding = np.array(json.loads(segment.embedding_vector))
```

---

### ⚠️ **Requirements**
1. SentenceTransformers installed:
   ```bash
   pip install sentence-transformers
   ```
2. NumPy for array handling

---

### 📊 **Performance Considerations**
- **Chunk Size**: 500-1500 chars recommended
- **Memory**: ~1MB per 1000 segments
- **Processing**: ~100ms per chunk on CPU

Would you like me to:
1. Add examples of querying with embeddings?
2. Document the model selection tradeoffs?
3. Include error handling recommendations?

### 🔄 **Data Flow**
1. Document uploaded → 2. Course created → 3. Modules generated →  
4. User interacts → 5. Progress updated → 6. Searchable content

===========================================================================

Here's the comprehensive documentation for your Vocabulary API endpoints:

---

## 📖 Vocabulary API Endpoints

### **Base URL**
`/api/vocabularies`

---

### ➕ Create Vocabulary Entry
`POST /api/create-vocabularies/{course_id}/`

#### **Description**
Creates a new vocabulary entry for a specific course.

#### **Parameters**
| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| `course_id` | integer | path | Yes | ID of the associated course |

#### **Responses**
- `200 OK`: Returns the created vocabulary entry
  ```json
  {
    "id": 1,
    "words": [
      {"term": "algorithm", "definition": "A set of rules..."}
    ],
    "course_id": 5
  }
  ```
- `500 Internal Server Error`: Creation failed
  ```json
  {
    "detail": "Error message"
  }
  ```

---

### 📚 Get Vocabulary Words
`GET /api/vocabularies/{course_id}/words`

#### **Description**
Retrieves all vocabulary words for a specific course.

#### **Parameters**
| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| `course_id` | integer | path | Yes | ID of the course |

#### **Responses**
- `200 OK`: Returns vocabulary words
  ```json
  {
    "words": [
      {"term": "variable", "definition": "A storage location..."},
      {"term": "function", "definition": "A reusable code block..."}
    ]
  }
  ```
- `500 Internal Server Error`: Retrieval failed
  ```json
  {
    "detail": "Error retrieving words: [error details]"
  }
  ```

---

### 🔍 Search Vocabulary
`GET /api/vocabularies/{course_id}/search`

#### **Description**
Searches for vocabulary terms within a course.

#### **Parameters**
| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| `course_id` | integer | path | Yes | ID of the course |
| `keyword` | string | query | Yes | Search term (min 1 character) |

#### **Responses**
- `200 OK`: Returns matching vocabulary words
  ```json
  {
    "words": [
      {"term": "database", "definition": "An organized collection..."}
    ]
  }
  ```
- `500 Internal Server Error`: Search failed
  ```json
  {
    "detail": "Search error: [error details]"
  }
  ```

---

### 🏷️ Data Schemas
#### **Vocabulary**
```json
{
  "id": "integer",
  "words": [
    {
      "term": "string",
      "definition": "string"
    }
  ],
  "course_id": "integer"
}
```

#### **VocabularyWords**
```json
{
  "words": [
    {
      "term": "string",
      "definition": "string"
    }
  ]
}
```

---

### Error Handling
All endpoints return standardized error responses:
- `500` status code for server errors
- JSON-formatted error details
- Original error message in development mode

---

### Example Usage
```bash
# Create vocabulary
curl -X POST http://localhost:8000/api/create-vocabularies/5/

# Get words
curl http://localhost:8000/api/vocabularies/5/words

# Search words
curl http://localhost:8000/api/vocabularies/5/search?keyword=variable
```


===========================================================================

Here's the comprehensive API documentation for your StudyAI backend routes:

---

# 📚 StudyAI API Documentation

## 🔐 **Authentication**
`POST /api/login`  
**Description**: Authenticate user and get JWT token  
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```
**Response**:
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

---

## 👥 **User Management**
| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/api/register` | POST | Register new user | `UserCreate` schema |
| `/api/get-users` | GET | List all users | - |
| `/api/get-user/{id}` | GET | Get user by ID | `id` (path) |
| `/api/user/update/{id}` | PUT | Update user | `id` (path), `UserCreate` schema |
| `/api/delete/user/{id}` | DELETE | Delete user | `id` (path) |

---

## 📄 **Document Processing**
### PDF Processing
`POST /api/extract-pdf-text`  
**Description**: Upload and process PDF  
**Parameters**:
- `file`: PDF file (UploadFile)
- `user_id`: Owner ID (query)

**Response**:
```json
{
  "document_id": 123,
  "extracted_text": "First 100 chars...",
  "storage_path": "temp_files/pdf/...",
  "simplified_text": "Simplified version...",
  "summary_text": "Condensed summary..."
}
```

### Image Processing
`POST /api/extract-text-from-image`  
**Tech Stack**: Uses Pytesseract for OCR  
**Error Cases**:
- `400`: Non-image file
- `500`: OCR processing failure

### Video Processing
`POST /api/extract-text-from-video`  
**Tech Stack**: FFmpeg (frame extraction) + Pytesseract (OCR)  
**Parameters**:
- `frames_per_second`: 1-10 (default: 1)

---

## 📚 **Course Management**
### Course Retrieval
| Endpoint | Description | Response |
|----------|-------------|----------|
| `GET /api/get-course/{course_id}` | Get full course | `Course` object |
| `GET /api/user/{user_id}/courses` | List user's courses | `List[Course]` |

### Module Access
```mermaid
graph LR
    A[Document] --> B(Simplified Modules)
    A --> C(Summary Modules)
    B --> D[GET /courses-doc/{id}/simplified-modules]
    C --> E[GET /courses-doc/{id}/summary-modules]
```

### Progress Tracking
`PUT /api/course/{course_id}/update-simplified-progress`  
**Body**:
```json
{"simplified_current_page": 3}
```

---

## 🔍 **Search Functionality**
### Course Search
`GET /courses/search`  
**Advanced Parameters**:
```http
/courses/search?query=math&fields=course_name,summary_text&fuzzy=true&skip=0&limit=5
```

### Vocabulary Search
`GET /courses/{course_id}/vocabulary/search`  
**Features**:
- Exact/partial term matching
- Definition searching
- Pagination

---

## 📖 **Vocabulary System**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/create-vocabularies/{course_id}` | POST | Generate vocabulary from course |
| `GET /api/vocabularies/{course_id}/words` | GET | Get all vocabulary words |
| `GET /courses/{course_id}/vocabulary/search` | GET | Advanced term search |

**Vocabulary Object**:
```json
{
  "term": "photosynthesis",
  "definition": "Process by which plants convert light energy..."
}
```

---

## 🛠 **Technical Stack**
| Functionality | Technology |
|--------------|------------|
| PDF Processing | PyMuPDF |
| Image OCR | Pytesseract |
| Video Processing | FFmpeg + OpenCV |
| Text Generation | Ollama LLM |
| Vector Storage | JSON-serialized embeddings |

---

## ⚠️ **Error Handling**
Standard error responses:
```json
{
  "detail": "Error message",
  "status_code": 400/404/500
}
```

---



===========================================================================

Here's the comprehensive documentation for your StudyAI schema definitions:

---

# 📝 StudyAI Schema Documentation

## 👤 **User Schemas**

### `UserBase`
```python
class UserBase(BaseModel):
    fullName: str
    email: str
    class_level: str
    password: str  # Will be hashed
    best_subjects: str
    learning_objectives: str
    academic_level: str
    statistic: int
```

### `UserCreate` (Registration)
- Inherits all fields from `UserBase`

### `User` (Response Model)
```python
class User(UserBase):
    id: int
    # Config enables ORM mode for SQLAlchemy
```

### Authentication
```python
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

---

## 📚 **Course Schemas**

### Enums
```python
class CourseLevelEnum(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
```

### `CourseBase`
```python
class CourseBase(BaseModel):
    course_name: str
    original_text: Optional[str]
    simplified_text: Optional[str]
    summary_text: Optional[str]
    level: CourseLevelEnum
    estimated_completion_time: Optional[str]
    # Module structures
    summary_modules: List[Dict] = []
    simplified_modules: List[Dict] = []
    # Pagination
    simplified_module_pages: int = 0
    summary_module_pages: int = 0
    # Progress tracking
    simplified_current_page: int = 1
    summary_current_page: int = 1
    simplified_module_statistic: float = 0.0
    summary_modules_statistic: float = 0.0
    document_id: int
```

### `Course` (Full Response)
```python
class Course(CourseBase):
    id_course: int
    created_at: datetime
    quizzes: List['Quiz'] = []
    vocabularies: List['Vocabulary'] = []
```

---

## ❓ **Quiz Schemas**

### Enums
```python
class QuizTypeEnum(str, Enum):
    qcm = "qcm"               # Multiple Choice
    texte = "texte"           # Free Text
    true_or_false = "true_or_false"
```

### `QuizBase`
```python
class QuizBase(BaseModel):
    course_id: int
    instruction: str
    question: str
    correct_answer: str
    choices: dict             # {"A": "Option 1", "B": "Option 2"}
    quiz_type: QuizTypeEnum
    level_of_difficulty: str  # Should be separate enum
    number_of_questions: int
```

### `Quiz` (Response)
```python
class Quiz(QuizBase):
    id: int
    created_at: datetime
    feedbacks: List['Feedback'] = []
```

---

## 📖 **Vocabulary Schemas**

### `VocabularyBase`
```python
class VocabularyBase(BaseModel):
    course_id: int
    words: List[Dict] = []    # [{"term": "Photosynthesis", "definition": "..."}]
```

### `VocabularyWords` (Response)
```python
class VocabularyWords(BaseModel):
    words: List[Dict]
```

### Search Responses
```python
class VocabularySearchResult(BaseModel):
    term: str
    definition: str

class VocabularySearchResponse(BaseModel):
    results: List[Dict]
    pagination: Dict[str, int]
```

---

## 💬 **Feedback Schema**

### `FeedbackBase`
```python
class FeedbackBase(BaseModel):
    quiz_id: int
    rating: int               # 1-5 scale
    comment: Optional[str]
```

### `Feedback` (Response)
```python
class Feedback(FeedbackBase):
    id: int
    created_at: datetime
```

---

## 📄 **Document Enums**

```python
class DocumentTypeEnum(str, Enum):
    pdf = "pdf"
    image = "image"
    video = "video"
```

---

### Key Features
1. **Progress Tracking**: Built-in statistics for course completion
2. **Modular Content**: Nested module structures for simplified/summary versions
3. **Type Safety**: Enums for fixed-value fields
4. **ORM Compatibility**: All models support SQLAlchemy conversion

### Example Usage
```python
# Creating a course
course_data = {
    "course_name": "Biology 101",
    "level": "beginner",
    "document_id": 123
}
CourseCreate(**course_data)
```


===========================================================================


Great — let’s walk through how to implement **custom Ollama behavior using a `Modelfile`**, step by step. You’re going to:

---

### ✅ Step 1: Create a Custom Model with a `Modelfile`

You’ll **store the `Modelfile` anywhere** on your machine where you can run terminal commands. Ideally, keep it in your project directory under a folder like `ollama-models/`.

---

### 📁 Directory structure example:

```
your-project/
├── app/
│   ├── main.py
│   └── ...
├── ollama-models/
│   └── Modelfile
├── .env
└── requirements.txt
```

---

### ✅ Step 2: Write the `Modelfile`

Create a new file named `Modelfile` in the `ollama-models/` directory with this content:

```Dockerfile
FROM llama2

SYSTEM """
You are a JSON-only assistant.

You must return all answers strictly as valid JSON, based on the exact structure provided in the prompt.

NEVER include markdown, extra text, or explanations. Only raw JSON is allowed in your output.

If anything is unclear, guess but keep the format. Never break JSON structure.
"""
```

---

### ✅ Step 3: Build the Custom Model

In your terminal, **navigate to the folder** with the `Modelfile`, then run:

```bash
cd ollama-models
ollama create json-llama2 -f Modelfile
```

If successful, you’ll see something like:

```
✔ created json-llama2 from llama2
```

---

### ✅ Step 4: Update `.env` to use the new model

Open your `.env` and change the model to:

```
OLLAMA_MODEL=json-llama2
```

This tells your app to use the custom model you just created.

---

### ✅ Step 5: Restart your app

Make sure to restart your FastAPI app or any dev server (like `uvicorn`) so it picks up the `.env` changes.

---

### 🔁 Result: Now Ollama will default to JSON output

Because of the `SYSTEM` instruction in your custom model, **even bad prompts** are more likely to return clean JSON. You can still reinforce this in your prompt as needed.

---

Would you like a ready-made shell script that automates model creation, so you can reuse it across projects?


===========================================================================


Here's a comprehensive documentation for your GitHub README that explains how to set up and use your OCR processing system:

# OCR Document Processing System

This system allows you to extract text from images and videos using Tesseract OCR and FFmpeg, then process the text for summarization and simplification using Ollama.

## Features

- Extract text from images (JPG, PNG, etc.)
- Extract text from video frames (MP4, MOV, AVI, MKV)
- Generate summaries of extracted text
- Create simplified versions of complex text
- Store processed documents with metadata
- Segment text for further processing

## Prerequisites

Before using this system, you need to install:

1. **Tesseract OCR** (v5.0+ recommended)
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Default install path: `C:\Program Files\Tesseract-OCR`

2. **FFmpeg** (for video processing)
   - Download from: https://ffmpeg.org/download.html
   - Default install path: `C:\ffmpeg\bin`

3. **Python** (v3.8+ recommended)

## Installation

1. Add the following paths to your system environment variables:
   ```
   C:\Program Files\Tesseract-OCR
   C:\ffmpeg\bin
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## API Endpoints

### Process Image

- **Endpoint**: `/process/image`
- **Method**: POST
- **Parameters**:
  - `file`: Image file (JPG, PNG, etc.)
  - `user_id`: ID of the uploading user

**Response**:
```json
{
  "document_id": 123,
  "user_id": 1,
  "filename": "example.jpg",
  "storage_path": "temp_files/images/20240502_1430_example.jpg",
  "extracted_text": "Sample extracted text...",
  "message": "Image processed successfully..."
}
```

### Process Video

- **Endpoint**: `/process/video`
- **Method**: POST
- **Parameters**:
  - `file`: Video file (MP4, MOV, AVI, MKV)
  - `user_id`: ID of the uploading user
  - `frames_per_second`: (Optional) Frames to process per second (default: 1)

**Response**:
```json
{
  "document_id": 124,
  "user_id": 1,
  "filename": "example.mp4",
  "storage_path": "temp_files/videos/20240502_1430_example.mp4",
  "extracted_text": "Sample text from video frames...",
  "message": "Video processed successfully..."
}
```

## How It Works

### Image Processing
1. User uploads an image file
2. System saves the image to temporary storage
3. Tesseract OCR extracts text from the image
4. Text is processed to generate:
   - A summary version
   - A simplified version
5. Results are stored in the database

### Video Processing
1. User uploads a video file
2. System saves the video to temporary storage
3. FFmpeg extracts frames at specified interval
4. Tesseract OCR processes each frame for text
5. Combined text is processed to generate:
   - A summary version
   - A simplified version
6. Results are stored in the database

## Configuration

### Environment Variables
Ensure these paths are set in your system environment:
- `TESSERACT_CMD`: Path to Tesseract executable (default: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
- `FFMPEG_PATH`: Path to FFmpeg binaries (default: `C:\ffmpeg\bin`)

### Storage Locations
- Images: `./temp_files/images/`
- Videos: `./temp_files/videos/`

## Troubleshooting

**OCR Failures:**
- Ensure Tesseract is properly installed
- Verify the environment path includes Tesseract
- Check image quality (OCR works best with clear, high-contrast text)

**FFmpeg Errors:**
- Verify FFmpeg installation
- Check the FFmpeg path in environment variables
- Ensure the video file is not corrupted

## Dependencies

- FastAPI
- SQLAlchemy
- Pytesseract
- Pillow (PIL)
- FFmpeg-python
- Python-multipart (for file uploads)

## License

[Specify your license here]

---

This documentation provides users with clear instructions on setting up and using your system. You may want to add:
1. Screenshots of example outputs
2. More detailed installation instructions for different OSes
3. Example curl commands for API testing
4. Information about the database schema
5. Configuration options for text processing

===========================================================================

Here's a comprehensive documentation for your GitHub README that covers both Google and Facebook authentication setup, ngrok configuration, and code explanation:

---

# OAuth Authentication Setup Guide

## Table of Contents
1. [Google OAuth Setup](#google-oauth-setup)
2. [Facebook Developer Setup](#facebook-developer-setup)
3. [Ngrok Configuration](#ngrok-configuration)
4. [Server Setup](#server-setup)
5. [Code Implementation](#code-implementation)
6. [Usage](#usage)

---

## Google OAuth Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project"
3. Name your project (e.g., "MyAuthApp")
4. Click "Create"

### 2. Enable OAuth API
1. Navigate to "APIs & Services" → "Library"
2. Search for "Google People API" and enable it
3. Search for "Google+ API" and enable it

### 3. Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Web application"
4. Add authorized JavaScript origins:
   - `http://localhost:8000`
   - `https://your-ngrok-url.ngrok-free.app`
5. Add authorized redirect URIs:
   - `http://localhost:8000/api/auth/google/callback`
   - `https://your-ngrok-url.ngrok-free.app/api/auth/google/callback`
6. Click "Create"
7. Note your:
   - **Client ID**
   - **Client Secret**

### 4. Configure Consent Screen
1. Go to "OAuth consent screen"
2. Select "External" user type
3. Fill in required app information
4. Add test users (your email)
5. Save and submit for verification (if going public)

---

## Facebook Developer Setup

### 1. Create Developer Account
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "Get Started" and register as a developer

### 2. Create New App
1. Go to "My Apps" → "Create App"
2. Select "Consumer" → "Next"
3. Enter display name (e.g., "MyAuthApp")
4. Create app ID

### 3. Configure Basic Settings
1. Go to "Settings" → "Basic"
2. Add contact email
3. Under "App Domains" add:
   - `localhost`
   - `your-ngrok-url.ngrok-free.app`

### 4. Add Facebook Login Product
1. Go to "Products" → "Add Product"
2. Select "Facebook Login"
3. Configure settings:
   - Valid OAuth Redirect URIs:
     - `https://your-ngrok-url.ngrok-free.app/api/auth/facebook/callback`
   - Enable "Client OAuth Login"
   - Enable "Web OAuth Login"

### 5. Get App Credentials
1. Note your:
   - **App ID**
   - **App Secret** (under "Settings" → "Basic")

---

## Ngrok Configuration

### 1. Install Ngrok
```bash
npm install -g ngrok  # Using npm
# OR
brew install ngrok    # macOS
choco install ngrok   # Windows
```

### 2. Start Ngrok Tunnel
```bash
ngrok http 8000
```
This will provide:
- Forwarding URL (e.g., `https://abc123.ngrok-free.app`)
- Web Interface (http://127.0.0.1:4041) for monitoring

### 3. Update All Configurations
Replace in all previous steps:
- `your-ngrok-url.ngrok-free.app` with your actual ngrok URL

---

## Server Setup

### 1. Environment Variables
Create `.env` file:
```env
# Google
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret

# Facebook
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_secret

# General
SECRET_KEY=your_secret_key_for_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. Start Development Server
```bash
# Install dependencies
pip install fastapi uvicorn python-dotenv requests passlib python-jose[cryptography]

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Code Implementation

### 1. Backend Structure
```
│   /google_auth.py       # Google auth routes
│   /facebook_auth.py     # Facebook auth routes
```

### 2. Google Auth (google.py)
```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .schemas import GoogleToken, TokenResponse

router = APIRouter(prefix="/api", tags=["Google Auth"])

@router.post("/login/google", response_model=TokenResponse)
async def google_login(google_token: GoogleToken):
    """
    Authenticates user with Google OAuth token
    1. Verifies token with Google API
    2. Creates/retrieves local user
    3. Returns JWT token
    """
    # Implementation...
```

### 3. Facebook Auth (facebook.py)
```python
from fastapi import APIRouter, Depends, HTTPException
from .schemas import FacebookToken, TokenResponse

router = APIRouter(prefix="/api")

@router.post("/login/facebook", response_model=TokenResponse)
async def facebook_login(fb_token: FacebookToken):
    """
    Authenticates user with Facebook token
    1. Verifies token with Facebook Graph API
    2. Creates/retrieves local user
    3. Returns JWT token
    """
    # Implementation...
```

### 4. Frontend Implementation
Key components in `static/auth.html`:
```javascript
// Google Login
function handleGoogleSignIn(response) {
    // Sends credential to /auth/google/login
}

// Facebook Login
FB.login(function(response) {
    // Sends accessToken to /auth/facebook/login
}, {scope: 'public_profile,email'});
```

---

## Usage

### 1. Development
1. Start backend server
2. Start ngrok tunnel
3. Access via: `https://your-ngrok-url.ngrok-free.app/static/auth.html`

### 2. Production
1. Replace ngrok URLs with your domain
2. Set up HTTPS certificates
3. Submit OAuth apps for verification

### 3. Testing
- Use test users in both platforms
- Monitor requests in ngrok web interface (http://localhost:4041)

---

## Security Notes
- Never commit `.env` to version control
- Regenerate secrets if compromised
- Limit OAuth scopes to minimum required
- Implement CSRF protection for production

For complete code examples, see the repository's source files. Each authentication method includes detailed error handling and validation.

===========================================================================

Great — here's a complete, clear, and production-ready **README documentation** section you can copy into your GitHub repo. It explains your Gemini API integration using the `gemini-2.5-flash-preview-04-17` model with flexible prompt handling.

---

## 🧠 Gemini API Integration

This project integrates with Google’s **Gemini 2.5 Flash** model (`gemini-2.5-flash-preview-04-17`) using the official `google-generativeai` SDK. The integration is designed to support various prompt types, including text and structured JSON generation (e.g., quizzes, summaries, glossaries).

---

### 🚀 Features

* Easy integration with **Google Gemini API**
* Supports:

  * Free-tier compatible model: `gemini-2.5-flash-preview-04-17`
  * Structured JSON and plain text responses
  * System prompts and flexible generation behavior
* Graceful fallback when quota is exceeded (optional)
* Ready for CLI, web app, or API backend use

---

### 📦 Installation

Install the required Google Generative AI SDK:

```bash
pip install google-generativeai
```

---

### 🔐 API Key Setup

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app)
2. Export it in your environment:

```bash
.env/ GOOGLE_API_KEY="your-api-key-here"
```

Or set it inline in code as a fallback (not recommended for production):

```python
os.environ["GOOGLE_API_KEY"] = "your-api-key-here"
```

---

### 🧩 Function: `generate_gemini_response`

```python
from utils.gemini_api import generate_gemini_response

response = generate_gemini_response(
    prompt="Write a short summary of the text...",
    model_name="gemini-2.5-flash-preview-04-17",  # Free-tier model
    response_type="json",  # or "text"
    system_prompt="You are a JSON-only assistant. Respond only with valid JSON."
)

print(response)
```

---

### 🔧 Function Definition

```python
def generate_gemini_response(
    prompt: str,
    model_name: str = "gemini-2.5-flash-preview-04-17",
    response_type: str = "text",  # "text" or "json"
    system_prompt: str = None
) -> str:
    """
    Generate a response from the Gemini model.

    Args:
        prompt (str): User prompt.
        model_name (str): Gemini model to use.
        response_type (str): "text" or "json".
        system_prompt (str): Optional system-level instruction.

    Returns:
        str: Raw text or JSON response.
    """
    import google.generativeai as genai
    import google.api_core.exceptions as gexc

    try:
        model = genai.GenerativeModel(model_name=model_name)
        chat = model.start_chat(history=[])
        if system_prompt:
            chat.send_message(system_prompt)

        gen_config = {"response_mime_type": "application/json"} if response_type == "json" else {}
        response = chat.send_message(prompt, generation_config=gen_config)
        return response.text

    except gexc.ResourceExhausted as e:
        print(f"[ERROR] Quota exhausted for {model_name}.")
        raise e
```

---

### ✅ Example Use Cases

#### 1. Generate JSON-based Quiz

```python
prompt = "Create a 3-question multiple choice quiz on BOI reporting..."
system_prompt = "You are a JSON-only assistant. Only output valid JSON."
response = generate_gemini_response(prompt, response_type="json", system_prompt=system_prompt)
```

#### 2. Summarize Content

```python
prompt = "Summarize the following text for beginners: ..."
response = generate_gemini_response(prompt, response_type="text")
```

---

### 📌 Notes

* This uses the **Gemini 2.5 Flash Preview model**, which is:

  * Fast and efficient
  * Free-tier friendly
  * Suitable for text generation, structured data output, and reasoning tasks
* Avoid using `gemini-2.5-pro-preview-05-06` unless your Google Cloud project has **billing enabled**

---

### 📚 References

* [Google Gemini API Documentation](https://ai.google.dev/)
* [Rate Limits & Quotas](https://ai.google.dev/gemini-api/docs/rate-limits)
* [MakerSuite Console](https://makersuite.google.com/app)

---

Would you like this turned into a `README.md` file directly? I can generate the full markdown source if you want to drop it in your repo.

===========================================================================

USER
──────
• id (Integer, PK)
• fullName (String)
• email (String, unique)
• password (String)
• best_subjects (String)
• learning_objectives (String)
• class_level (String)
• academic_level (String)
• statistic (Integer)
• created_at (DateTime)
│
└─── 1:* ───► DOCUMENT
              ──────
              • id_document (Integer, PK)
              • title (String)
              • type_document (String)
              • original_filename (String)
              • storage_path (String)
              • original_text (String)
              • uploaded_at (DateTime)
              • user_id (Integer, FK→Users.id)
              │
              ├─── 1:* ───► COURSE
              │            ──────
              │            • id_course (Integer, PK)
              │            • course_name (String)
              │            • original_text (String)
              │            • simplified_text (String)
              │            • summary_text (String)
              │            • level_of_difficulty (Enum)
              │            • estimated_completion_time (String)
              │            • quiz_instruction (String)
              │            • summary_modules (JSON)
              │            • simplified_modules (JSON)
              │            • simplified_module_pages (Integer)
              │            • summary_module_pages (Integer)
              │            • simplified_current_page (Integer)
              │            • summary_current_page (Integer)
              │            • simplified_module_statistic (Numeric)
              │            • summary_modules_statistic (Numeric)
              │            • document_id (Integer, FK→Documents.id_document)
              │            • created_at (DateTime)
              │            │
              │            ├─── 1:* ───► QUIZ
              │            │            ──────
              │            │            • id_quiz (Integer, PK)
              │            │            • course_id (Integer, FK→Courses.id_course)
              │            │            • question (String)
              │            │            • correct_answer (String)
              │            │            • user_answer (String)
              │            │            • choices (JSON)
              │            │            • quiz_type (Enum)
              │            │            • level_of_difficulty (Enum)
              │            │            • number_of_questions (Integer)
              │            │            • created_at (DateTime)
              │            │
              │            ├─── 1:* ───► VOCABULARY
              │            │            ──────
              │            │            • id_term (Integer, PK)
              │            │            • course_id (Integer, FK→Courses.id_course)
              │            │            • words (JSON)
              │            │            • created_at (DateTime)
              │            │
              │            └─── 1:* ───► FEEDBACK
              │                         ──────
              │                         • id_feedback (Integer, PK)
              │                         • course_id (Integer, FK→Courses.id_course)
              │                         • rating (Integer)
              │                         • comment (String)
              │                         • created_at (DateTime)
              │
              └─── 1:* ───► SEGMENT
                          ──────
                          • id_segment (Integer, PK)
                          • document_id (Integer, FK→Documents.id_document)
                          • raw_text (String)
                          • embedding_vector (String)
                          • created_at (DateTime)