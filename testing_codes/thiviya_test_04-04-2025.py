import os
import hashlib
import chromadb
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import PyPDF2

# Load embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Initialize ChromaDB with persistent storage
chroma_client = chromadb.PersistentClient(path="./vector_store")
collection = chroma_client.get_or_create_collection(name="pdf_embeddings")

# Load the TinyLlama model for text generation
qa_pipeline = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Error: The file '{pdf_path}' does not exist.")
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    if not text.strip():
        raise ValueError(f"Error: No text could be extracted from '{pdf_path}'.")
    return text

def get_pdf_hash(pdf_path):
    """Generate a unique hash for the PDF file based on its content."""
    sha256_hash = hashlib.sha256()
    with open(pdf_path, "rb") as f:
        while chunk := f.read(8192):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def store_pdf_in_vector_db(pdf_paths):
    """Stores text from PDFs as embeddings in ChromaDB using upsert to avoid duplication."""
    for pdf_path in pdf_paths:
        pdf_hash = get_pdf_hash(pdf_path)
        # Extract text from the PDF
        text = extract_text_from_pdf(pdf_path)
        # Generate embedding
        embedding = embedding_model.encode([text])[0]

        # Upsert document to prevent duplicate entries
        collection.upsert(
            ids=[pdf_hash],  # Using PDF hash as a unique ID
            embeddings=[embedding.tolist()],
            documents=[text]
        )
        print(f"Stored content from '{os.path.basename(pdf_path)}' in ChromaDB!")

def retrieve_first_n_lines(n=100):
    """Retrieve the first n lines of the stored PDF from the vector database."""
    result = collection.get()
    if result and "documents" in result and result["documents"]:
        full_text = result["documents"][0]  # Get the first stored document
        lines = full_text.strip().split("\n")
        first_n_lines = "\n".join(lines[:n])
        print("\nRetrieved Text from Vector (First {} lines):\n".format(n))
        print(first_n_lines)
        return first_n_lines
    else:
        print("No stored documents found in the vector database.")
        return ""

def generate_questions(text):
    """Generate questions based on the given text using TinyLlama."""
    if not text:
        print("No text available for question generation.")
        return
    print("\nGenerating questions...\n")
    # Modify prompt for better question generation
    prompt = f"Read the following text and generate 5 questions:\n{text}\nQuestions:"
    # Use text-generation pipeline with max_new_tokens
    questions = qa_pipeline(prompt, max_new_tokens=500)
    # Print the generated questions
    print(questions[0]['generated_text'])

if _name_ == "_main_":
    pdf_files = ["html_ref.pdf"]  # Specify the PDF files
    store_pdf_in_vector_db(pdf_files)
    retrieved_text = retrieve_first_n_lines(1000)
    generate_questions(retrieved_text) 