from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from pdf_processing import extract_text_from_all_pdfs
from embedding_store import qdrant, embedding_model
import config  # Import the config file
import torch
from accelerate import init_empty_weights

torch.cuda.empty_cache()

# Load QA Model with 8-bit quantization
quantization_config = BitsAndBytesConfig(llm_int8_enable_fp32_cpu_offload=True)
qa_tokenizer = AutoTokenizer.from_pretrained(config.QA_MODEL)
qa_model = AutoModelForCausalLM.from_pretrained(
    config.QA_MODEL,
    device_map="auto",  # Automatically map to GPU if available
    quantization_config=quantization_config
)
qa_pipeline = pipeline("text-generation", model=qa_model, tokenizer=qa_tokenizer)

# Load Summarization Model with 8-bit quantization
summarization_tokenizer = AutoTokenizer.from_pretrained(config.SUMMARIZATION_MODEL)
summarization_model = AutoModelForSeq2SeqLM.from_pretrained(
    config.SUMMARIZATION_MODEL,
    device_map="auto",  # Automatically map to GPU if available
    load_in_8bit=True   # Enable 8-bit quantization
)
summarization_pipeline = pipeline("summarization", model=summarization_model, tokenizer=summarization_tokenizer)

def retrieve_legal_knowledge(query):
    """Retrieves relevant legal knowledge from Qdrant."""
    vector = embedding_model.encode([query]).tolist()[0]
    
    search_result = qdrant.query_points(
        collection_name=config.COLLECTION_NAME,  # Use COLLECTION_NAME from config
        query=vector,
        with_payload=True,
        limit=5
    ).points

    retrieved_texts = [point.payload["text"] for point in search_result if "text" in point.payload]
    return " ".join(retrieved_texts)

def summarize_document(pdf_path):
    """Summarizes the uploaded user document (Doc 2)."""
    doc_text = str(extract_text_from_all_pdfs(pdf_path))
    print("type of doc text : " ,type(doc_text))
    print("doc text : ", doc_text)
    retrieved_legal_knowledge = str(retrieve_legal_knowledge(doc_text))
    
    print("Retrieved Legal Knowledge:", retrieved_legal_knowledge)
    print("Type:", type(retrieved_legal_knowledge))
    
    combined_text = retrieved_legal_knowledge + "\n" + doc_text
    summary = summarization_pipeline(combined_text, max_length=300, min_length=100, do_sample=False)
    
    return summary[0]["summary_text"]

def answer_legal_question(query, pdf_path):
    """Answers legal questions based on Doc 2 using legal knowledge."""
    doc_summary = summarize_document(pdf_path)
    retrieved_legal_knowledge = retrieve_legal_knowledge(query)
    
    prompt = f"User Query: {query}\nLegal Context: {retrieved_legal_knowledge}\nDocument Summary: {doc_summary}\nAnswer:"
    
    response = qa_pipeline(prompt, max_length=200, do_sample=True)
    return response[0]["generated_text"]


# Example usage
if __name__ == "__main__":
    pdf_path = "D:/Data_Aces/Codes/ai_legal_assistant/data/user_uploads"  # Replace with your actual PDF path
    query = "What are the three ways in which a person can be said to abet the doing of a thing under the law of abetment?"
    
    summary = summarize_document(pdf_path)
    print("Summary:", summary)
    
    answer = answer_legal_question(query, pdf_path)
    print("Answer:", answer) 
    