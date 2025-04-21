import sys
sys.path.append('D:/Data_Aces/Codes/ai_legal_assistant/src')

from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from .pdf_processing import extract_text_from_all_pdfs, extract_text_from_pdf
from .embedding_store import qdrant, embedding_model
from .config import QDRANT_URL, EMBEDDING_MODEL, COLLECTION_NAME, QA_MODEL, SUMMARIZATION_MODEL
import torch
from accelerate import init_empty_weights

torch.cuda.empty_cache()

# Load Model with 8-bit quantization
class ModelRegistry:
    def __init__(self):
        self.qa_pipeline = None
        self.summarization_pipeline = None

    def load_models(self):
        print("🚀 Loading QA and Summarization models...")

        quantization_config = BitsAndBytesConfig(llm_int8_enable_fp32_cpu_offload=True)

        # Load QA model
        qa_tokenizer = AutoTokenizer.from_pretrained(QA_MODEL)
        qa_model = AutoModelForCausalLM.from_pretrained(
            QA_MODEL,
            device_map="auto",
            quantization_config=quantization_config
        )
        self.qa_pipeline = pipeline("text-generation", model=qa_model, tokenizer=qa_tokenizer)

        # Load Summarization model
        summarization_tokenizer = AutoTokenizer.from_pretrained(SUMMARIZATION_MODEL)
        summarization_model = AutoModelForSeq2SeqLM.from_pretrained(
            SUMMARIZATION_MODEL,
            device_map="auto",
            load_in_8bit=True
        )
        self.summarization_pipeline = pipeline("summarization", model=summarization_model, tokenizer=summarization_tokenizer)

        print("✅ Models loaded.")

# Singleton object
model_registry = ModelRegistry()
def retrieve_legal_knowledge(query):
    """Retrieves relevant legal knowledge from Qdrant."""
    vector = embedding_model.encode([query]).tolist()[0]
    
    search_result = qdrant.query_points(
        collection_name=COLLECTION_NAME,  # Use COLLECTION_NAME from config
        query=vector,
        with_payload=True,
        limit=5
    ).points

    retrieved_texts = [point.payload["text"] for point in search_result if "text" in point.payload]
    return " ".join(retrieved_texts)

def summarize_document(pdf_path):
    """Summarizes the uploaded user document (Doc 2) using chunking."""
    doc_text = extract_text_from_pdf(pdf_path)
    retrieved_legal_knowledge = retrieve_legal_knowledge(doc_text)

    combined_text = str(retrieved_legal_knowledge) + "\n" + str(doc_text)

    tokenizer = model_registry.summarization_pipeline.tokenizer
    model_max_length = tokenizer.model_max_length or 512  # Usually 512

    # Tokenize and split into chunks
    input_tokens = tokenizer.encode(combined_text)
    chunks = [input_tokens[i:i + model_max_length] for i in range(0, len(input_tokens), model_max_length)]

    # Summarize each chunk
    summaries = []
    for chunk in chunks:
        chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
        summary = model_registry.summarization_pipeline(
            chunk_text,
            max_length=300,
            min_length=100,
            do_sample=False
        )
        summaries.append(summary[0]["summary_text"])

    # Optional: Combine summaries and re-summarize them if it's too long
    final_summary_input = " ".join(summaries)
    if len(tokenizer.encode(final_summary_input)) > model_max_length:
        final_chunks = [tokenizer.decode(tokenizer.encode(final_summary_input)[i:i + model_max_length], skip_special_tokens=True)
                        for i in range(0, len(tokenizer.encode(final_summary_input)), model_max_length)]

        final_summaries = []
        for chunk in final_chunks:
            summary = model_registry.summarization_pipeline(
                chunk,
                max_length=300,
                min_length=100,
                do_sample=False
            )
            final_summaries.append(summary[0]["summary_text"])

        return " ".join(final_summaries)
    
    return final_summary_input



def answer_legal_question(query, pdf_path):
    """Answers legal questions based on Doc 2 using legal knowledge."""
    doc_summary = summarize_document(pdf_path)
    retrieved_legal_knowledge = retrieve_legal_knowledge(query)
    
    prompt = f" User Query: {query}\nLegal Context: {retrieved_legal_knowledge}\nDocument Summary: {doc_summary}\nAnswer:"
    
    response = model_registry.qa_pipeline(prompt, max_length=200, do_sample=True)
    return response[0]["generated_text"]


# Example usage
if __name__ == "__main__":
    pdf_path = "D:/Data_Aces/Codes/ai_legal_assistant/data/user_uploads"  # Replace with your actual PDF path
    query = "What are the three ways in which a person can be said to abet the doing of a thing under the law of abetment?"
    
    summary = summarize_document(pdf_path)
    print("Summary:", summary)
    
    #answer = answer_legal_question(query, pdf_path)
    #print("Answer:", answer)
