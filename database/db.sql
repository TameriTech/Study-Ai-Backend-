-- Create ENUM types using your model's naming
CREATE TYPE "DocumentType" AS ENUM ('pdf', 'image', 'video');
CREATE TYPE "QuizEnumType" AS ENUM ('mcq', 'text', 'true_or_false');
CREATE TYPE "QuizDifficultyLevel" AS ENUM ('easy', 'medium', 'hard');

-- Users table
CREATE TABLE "Users" (
    id SERIAL PRIMARY KEY,
    fullName VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    best_subjects VARCHAR(255),
    learning_objectives VARCHAR(255),
    class_level VARCHAR(255),
    academic_level VARCHAR(255),
    statistic INTEGER,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE "Documents" (
    id_document SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    type_document "DocumentType",
    original_filename VARCHAR(255) NOT NULL,
    storage_path VARCHAR(255) NOT NULL,
    original_text TEXT,
    uploaded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES "Users"(id) ON DELETE CASCADE
);

-- Courses table
CREATE TABLE "Courses" (
    id_course SERIAL PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    original_text TEXT,
    simplified_text TEXT,
    summary_text TEXT,
    level_of_difficulty "QuizDifficultyLevel",
    estimated_completion_time VARCHAR(50),
    quiz_instruction TEXT,
    summary_modules JSONB,
    simplified_modules JSONB,
    simplified_current_page INTEGER DEFAULT 1,
    summary_current_page INTEGER DEFAULT 1,
    simplified_module_pages INTEGER DEFAULT 0,
    summary_module_pages INTEGER DEFAULT 0,
    simplified_module_statistic NUMERIC(10, 2) DEFAULT 0,
    summary_modules_statistic NUMERIC(10, 2) DEFAULT 0,
    document_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES "Documents"(id_document) ON DELETE CASCADE
);

-- Segments table
CREATE TABLE "Segments" (
    id_segment SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    raw_text TEXT NOT NULL,
    embedding_vector TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES "Documents"(id_document) ON DELETE CASCADE
);

-- Quizzes table
CREATE TABLE "Quizzes" (
    id_quiz SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    user_answer TEXT,
    choices JSONB NOT NULL,
    quiz_type "QuizEnumType" NOT NULL,
    level_of_difficulty "QuizDifficultyLevel" NOT NULL,
    number_of_questions INTEGER,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES "Courses"(id_course) ON DELETE CASCADE
);

-- Vocabularies table
CREATE TABLE "Vocabularies" (
    id_term SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL,
    words JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES "Courses"(id_course) ON DELETE CASCADE
);

-- Feedbacks table
CREATE TABLE "Feedbacks" (
    id_feedback SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES "Courses"(id_course) ON DELETE CASCADE
);

-- Indexes for optimization
CREATE INDEX idx_documents_user_id ON "Documents"(user_id);
CREATE INDEX idx_courses_document_id ON "Courses"(document_id);
CREATE INDEX idx_segments_document_id ON "Segments"(document_id);
CREATE INDEX idx_quizzes_course_id ON "Quizzes"(course_id);
CREATE INDEX idx_vocabularies_course_id ON "Vocabularies"(course_id);
CREATE INDEX idx_feedbacks_course_id ON "Feedbacks"(course_id);
