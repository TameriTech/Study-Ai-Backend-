from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from typing import List


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# This function extracts text from a PDF file using the PyPDF library.
# It reads the PDF file and concatenates the text from all pages into a single string.
def extract_text_from_pdf(file) -> str:
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# This function splits the text into chunks of a specified maximum length.
# It ensures that the chunks are split at paragraph boundaries to maintain readability.
def chunk_text(text: str, max_length: int = 500) -> List[str]:
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) <= max_length:
            current_chunk += " " + para
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


# This function generates embeddings for a list of text chunks using the SentenceTransformer model.
# The embeddings are used for semantic search and similarity matching.
# Chargement du modèle (tu peux le placer en global dans le fichier)
def generate_embeddings(chunks: list) -> list:
    embeddings = embedding_model.encode(chunks, convert_to_numpy=True)
    return embeddings
