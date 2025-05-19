import os
import requests
from datetime import datetime
from typing import List, Optional
from google import genai
import chromadb
from chromadb.utils import embedding_functions
import PyPDF2
import docx
import textract

class RAGGeminiChatbot:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize RAG chatbot with Nomic embeddings via Ollama
        
        Args:
            api_key: Gemini API key (or set GEMINI_API_KEY environment variable)
            model: Gemini model name (default: gemini-1.5-flash)
        """
        # Validate and set API key
        self.api_key = "AIzaSyCOAGOoCTnHOya6i9v0_ZetHiUKFq6CpxA"
        if not self.api_key:
            raise ValueError("API key not provided and GEMINI_API_KEY environment variable not set")
        
        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model = model
        self.chat = None
        
        # Configuration
        self.system_instruction = "You are a helpful AI assistant with access to knowledge documents. Use retrieved information when relevant."
        self.show_timestamps = True
        self.supported_doc_types = ['.pdf', '.docx', '.txt', '.pptx']
        self.chunk_size = 2048  # Optimal for Nomic embeddings
        self.top_k = 3  # Number of relevant chunks to retrieve
        
        # Initialize vector database
        self._initialize_vector_db()
        
    def _initialize_vector_db(self):
        """Initialize ChromaDB with Nomic embeddings with robust error handling"""
        try:
            # Verify Ollama is running and model is available
            self._verify_ollama()
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=os.path.join(os.getcwd(), "chroma_db"))
            
            # Clean up any existing collection
            try:
                self.chroma_client.delete_collection("knowledge_base")
            except ValueError:
                pass  # Collection didn't exist
                
            # Create new collection with Nomic embeddings
            self.embedding_function = embedding_functions.OllamaEmbeddingFunction(
                model_name="nomic-embed-text",
                url="http://localhost:11434/api/embeddings",
                ollama_headers={"Content-Type": "application/json"}
            )
            
            self.collection = self.chroma_client.get_or_create_collection(
                name="knowledge_base",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}  # Better for semantic search
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize vector database: {str(e)}")
    
    def _verify_ollama(self):
        """Verify Ollama is running and nomic-embed-text is available"""
        try:
            # Check Ollama server status
            health_response = requests.get(
                "http://localhost:11434",
                timeout=10
            )
            if health_response.status_code != 200:
                raise ConnectionError("Ollama server not responding properly")
            
            # Verify model is available
            model_response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": "test"},
                timeout=30
            )
            if model_response.status_code != 200:
                raise ValueError("nomic-embed-text model not available in Ollama")
                
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Could not connect to Ollama: {str(e)}. Please ensure Ollama is running and the nomic-embed-text model is installed.")
    
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
        
    def process_command(self, command: str) -> Optional[bool]:
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
            try:
                self.load_document(file_path)
            except Exception as e:
                print(f"Error loading document: {str(e)}")
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
        
    def format_message(self, text: str, role: str) -> str:
        """Format message with optional timestamp"""
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] " if self.show_timestamps else ""
        role_prefix = "You: " if role == "user" else "AI: "
        return f"{timestamp}{role_prefix}{text}"
    
    def load_document(self, file_path: str):
        """Load and process a document with enhanced error handling"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self.supported_doc_types:
            raise ValueError(f"Unsupported file type {ext}. Supported types: {', '.join(self.supported_doc_types)}")
        
        print(f"Loading document: {os.path.basename(file_path)}...")
        try:
            text = self._extract_text(file_path)
            if not text:
                raise ValueError("Failed to extract text from document")
                
            chunks = self._chunk_text(text)
            document_id = os.path.basename(file_path)
            
            # Store in ChromaDB with progress indication
            total_chunks = len(chunks)
            print(f"Processing {total_chunks} chunks...", end="", flush=True)
            
            self.collection.add(
                documents=chunks,
                metadatas=[{"source": document_id} for _ in chunks],
                ids=[f"{document_id}_{i}" for i in range(len(chunks))]
            )
            
            print(f"\rSuccessfully loaded {total_chunks} chunks from {document_id}")
            
        except Exception as e:
            print(f"\nError loading document: {str(e)}")
            raise
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from various document formats"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        try:
            if ext == '.pdf':
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    return "\n".join([page.extract_text() for page in reader.pages])
            elif ext == '.docx':
                doc = docx.Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif ext == '.pptx':
                return textract.process(file_path).decode('utf-8')
            else:
                raise ValueError(f"Unsupported file type: {ext}")
        except Exception as e:
            raise RuntimeError(f"Error processing {file_path}: {str(e)}")
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into semantically meaningful chunks"""
        # First split by paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para.split())
            
            if current_length + para_length > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
                
            current_chunk.append(para)
            current_length += para_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks
    
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
    
    def retrieve_relevant_info(self, query: str) -> List[str]:
        """Retrieve relevant information with enhanced error handling"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=self.top_k,
                include=["documents", "distances"]
            )
            
            if not results['documents']:
                return []
                
            # Filter out low-quality matches
            min_distance = 0.3  # Adjust based on your needs
            relevant_chunks = [
                doc for doc, dist in zip(results['documents'][0], results['distances'][0])
                if dist < min_distance
            ]
            
            return relevant_chunks if relevant_chunks else []
            
        except Exception as e:
            print(f"Warning: Retrieval failed - {str(e)}")
            return []
    
    def generate_response(self, user_input: str) -> str:
        """Generate response using RAG with fallback mechanism"""
        try:
            # Retrieve relevant context
            context_chunks = self.retrieve_relevant_info(user_input)
            context = "\n".join([f"- {chunk}" for chunk in context_chunks]) if context_chunks else None
            
            # Prepare prompt
            prompt = f"""User question: {user_input}"""
            
            if context:
                prompt = f"""Context from knowledge base:
{context}

{prompt}"""
            
            # Generate response
            response = self.chat.send_message(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3  # More focused responses
                )
            )
            
            return response.text
            
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."

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
    print("RAG-Enhanced Gemini Chatbot with Nomic Embeddings")
    print("------------------------------------------------")
    
    try:
        chatbot = RAGGeminiChatbot()
        chatbot.run()
    except Exception as e:
        print(f"Failed to start chatbot: {str(e)}")
        print("Possible solutions:")
        print("- Ensure Ollama is running with 'ollama serve'")
        print("- Verify nomic-embed-text is installed with 'ollama pull nomic-embed-text'")
        print("- Check your Gemini API key is set")