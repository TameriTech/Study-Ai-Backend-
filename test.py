from google import genai
import os
from datetime import datetime
from typing import List, Dict, Optional
import chromadb
from chromadb.utils import embedding_functions
import PyPDF2
import docx
import textract

class RAGGeminiChatbot:
    def __init__(self, api_key=None, model="gemini-1.5-flash"):
        """
        Initialize the RAG-enhanced chatbot with Nomic embeddings
        """
        self.api_key = "AIzaSyCOAGOoCTnHOya6i9v0_ZetHiUKFq6CpxA"
        if not self.api_key:
            raise ValueError("API key not provided and GEMINI_API_KEY environment variable not set")
            
        self.client = genai.Client(api_key=self.api_key)
        self.model = model
        self.chat = None
        self.system_instruction = "You are a helpful AI assistant with access to knowledge documents. Use retrieved information when relevant."
        self.show_timestamps = True
        
        # Initialize ChromaDB with Nomic embeddings via Ollama
        self.embedding_function = embedding_functions.OllamaEmbeddingFunction(
            model_name="nomic-embed-text",
            url="http://localhost:11434/api/embeddings"  # Default Ollama endpoint
        )
        
        # Create or get the collection
        self.chroma_client = chromadb.PersistentClient(path="chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="knowledge_base",
            embedding_function=self.embedding_function
        )
        
        # Document processing settings
        self.supported_doc_types = ['.pdf', '.docx', '.txt', '.pptx']
        self.chunk_size = 1000  # Adjust based on your needs
        
    def start_chat(self):
        """Initialize a new chat session"""
        self.chat = self.client.chats.create(
            model=self.model,
            config=genai.types.GenerateContentConfig(
                system_instruction=self.system_instruction
            )
        )
        print("\nNew RAG-enhanced chat session started. Type 'quit' to exit or '/help' for commands.\n")
        
    def display_help(self):
        """Show available commands"""
        help_text = """
        Available Commands:
        /help - Show this help message
        /new - Start a new chat session
        /system <instruction> - Change system instruction
        /time [on|off] - Toggle message timestamps
        /load <file_path> - Load a document into the knowledge base
        /list - List loaded documents
        /clear - Clear the knowledge base
        /quit - Exit the chatbot
        """
        print(help_text)
        
    def process_command(self, command):
        """Handle user commands"""
        if command.startswith("/system "):
            self.system_instruction = command[8:]
            print(f"System instruction updated to: {self.system_instruction}")
            return True
        elif command == "/new":
            self.start_chat()
            return True
        elif command == "/help":
            self.display_help()
            return True
        elif command.startswith("/time"):
            parts = command.split()
            if len(parts) > 1:
                self.show_timestamps = parts[1].lower() == "on"
            else:
                self.show_timestamps = not self.show_timestamps
            print(f"Timestamps {'enabled' if self.show_timestamps else 'disabled'}")
            return True
        elif command.startswith("/load "):
            file_path = command[6:]
            self.load_document(file_path)
            return True
        elif command == "/list":
            self.list_documents()
            return True
        elif command == "/clear":
            self.clear_knowledge_base()
            return True
        elif command == "/quit":
            return False
        return None
        
    def format_message(self, text, role):
        """Format message with optional timestamp"""
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] " if self.show_timestamps else ""
        role_prefix = "You: " if role == "user" else "AI: "
        return f"{timestamp}{role_prefix}{text}"
    
    def extract_text_from_document(self, file_path: str) -> str:
        """Extract text from various document formats"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        try:
            if ext == '.pdf':
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = "\n".join([page.extract_text() for page in reader.pages])
            elif ext == '.docx':
                doc = docx.Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif ext == '.pptx':
                text = textract.process(file_path).decode('utf-8')
            else:
                raise ValueError(f"Unsupported file type: {ext}")
            return text
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into manageable chunks"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > chunk_size:  # +1 for space
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(word)
            current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks
    
    def load_document(self, file_path: str):
        """Load a document into the knowledge base"""
        if not os.path.exists(file_path):
            print(f"Error: File not found - {file_path}")
            return
            
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self.supported_doc_types:
            print(f"Error: Unsupported file type {ext}. Supported types: {', '.join(self.supported_doc_types)}")
            return
            
        print(f"Loading document: {file_path}...")
        text = self.extract_text_from_document(file_path)
        if not text:
            print("Failed to extract text from document")
            return
            
        chunks = self.chunk_text(text)
        document_id = os.path.basename(file_path)
        
        # Store in ChromaDB
        self.collection.add(
            documents=chunks,
            metadatas=[{"source": document_id} for _ in chunks],
            ids=[f"{document_id}_{i}" for i in range(len(chunks))]
        )
        
        print(f"Document loaded successfully with {len(chunks)} chunks")
    
    def list_documents(self):
        """List all documents in the knowledge base"""
        results = self.collection.get()
        if not results['documents']:
            print("Knowledge base is empty")
            return
            
        sources = set()
        for metadata in results['metadatas']:
            sources.add(metadata['source'])
            
        print("Documents in knowledge base:")
        for doc in sorted(sources):
            print(f"- {doc}")
    
    def clear_knowledge_base(self):
        """Clear all documents from the knowledge base"""
        self.collection.delete()
        print("Knowledge base cleared")
    
    def retrieve_relevant_info(self, query: str, n_results: int = 3) -> List[str]:
        """Retrieve relevant information from knowledge base using Nomic embeddings"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            print(f"Error in retrieval: {str(e)}")
            return []
    
    def generate_response(self, user_input: str) -> str:
        """Generate response using RAG approach"""
        # First retrieve relevant information
        retrieved_info = self.retrieve_relevant_info(user_input)
        
        # Prepare context for the model
        context = ""
        if retrieved_info:
            context = "Relevant information from knowledge base:\n"
            context += "\n".join([f"- {info}" for info in retrieved_info])
            context += "\n\n"
        
        # Generate response
        response = self.chat.send_message(
            f"{context}User question: {user_input}\n\n"
            "Please answer the question using the provided context when relevant. "
            "If the context doesn't contain relevant information, use your general knowledge."
        )
        
        return response.text
    
    def run(self):
        """Main chat loop"""
        self.start_chat()
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                    
                # Check for commands
                if user_input.startswith("/"):
                    should_continue = self.process_command(user_input)
                    if should_continue is False:
                        break
                    elif should_continue is True:
                        continue
                        
                # Generate response with RAG
                response_text = self.generate_response(user_input)
                
                # Print AI response
                print(self.format_message(response_text, "model"))
                
            except KeyboardInterrupt:
                print("\nUse '/quit' to exit or press Ctrl+C again to force quit.")
                try:
                    input()  # Wait for user to press enter
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Starting a new chat session...")
                self.start_chat()

if __name__ == "__main__":
    print("RAG-Enhanced Gemini Terminal Chatbot")
    print("-----------------------------------")
    
    try:
        chatbot = RAGGeminiChatbot()
        chatbot.run()
    except Exception as e:
        print(f"Failed to start chatbot: {str(e)}")