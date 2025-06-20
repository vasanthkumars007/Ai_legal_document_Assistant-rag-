import sys
sys.path.append('D:/Data_Aces/Codes/ai_legal_assistant/backend/src')

from transformers import AutoModelForQuestionAnswering, AutoModelForSeq2SeqLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from .pdf_processing import extract_text_from_all_pdfs, extract_text_from_pdf
from .embedding_store import qdrant, embedding_model
from .config import QDRANT_URL, EMBEDDING_MODEL, COLLECTION_NAME, QA_MODEL, SUMMARIZATION_MODEL
import torch
from accelerate import init_empty_weights
import re

torch.cuda.empty_cache()

class ModelRegistry:
    def __init__(self):
        self.qa_pipeline = None
        self.summarization_pipeline = None

    def load_models(self):
        print(" Loading QA and Summarization models...")

        # Load QA model (Extractive QA)
        # Load TinyLlama for QA (Text Generation for answering questions)
        self.qa_pipeline = pipeline(
            "text-generation", 
            model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", 
            torch_dtype=torch.bfloat16, 
            device_map="auto"
        )



        # Load Summarization model
        summarization_tokenizer = AutoTokenizer.from_pretrained(SUMMARIZATION_MODEL)
        summarization_model = AutoModelForSeq2SeqLM.from_pretrained(
            SUMMARIZATION_MODEL,
            device_map="auto",
        ) 
        self.summarization_pipeline = pipeline("summarization", model=summarization_model, tokenizer=summarization_tokenizer)

        print("✅ Models loaded.")

# Singleton object
model_registry = ModelRegistry()
def retrieve_legal_knowledge(query,limit=5):
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
    """Summarizes the uploaded user document (Doc 2) using TinyLlama with legal-specific prompt and chunking."""

    # Step 1: Extract document text and retrieve relevant legal knowledge
    doc_text = extract_text_from_pdf(pdf_path)
    retrieved_legal_knowledge = retrieve_legal_knowledge(doc_text)

    combined_text = str(retrieved_legal_knowledge) + "\n" + str(doc_text)

    # Step 2: Prepare tokenizer and chunking parameters
    tokenizer = model_registry.qa_pipeline.tokenizer
    model_max_length = getattr(tokenizer, "model_max_length", 2048)
    safe_chunk_length = min(model_max_length, 1024)  # safer, to fit prompt overhead

    input_tokens = tokenizer.encode(combined_text, truncation=False)
    chunks = [input_tokens[i:i + safe_chunk_length] for i in range(0, len(input_tokens), safe_chunk_length)]

    summaries = []
    for chunk in chunks:
        chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)

        # Step 3: Prepare legal-specific summarization prompt (similar to your qa_pipeline style)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a highly skilled legal assistant. Your task is to summarize legal documents in a clear and structured way.\n\n"
                    "**Your summary must begin by explicitly identifying:**\n"
                    "• From: The person or organization that issued the notice\n"
                    "• To: The person or organization that received the notice\n\n"
                    "Do not infer names — only include them if clearly mentioned. If the names are not mentioned, write 'Not specified'.\n\n"
                    "Then continue the summary under these sections:\n"
                    "1. Parties Involved  Briefly describe the roles (e.g., employee, employer)\n"
                    "2. Key Legal Issues  Summarize the main legal matters raised\n"
                    "3. Main Demands or Obligations  Summarize what the issuer is asking for or asserting\n"
                    "4. Actions Required / Deadlines  Mention any actions demanded or deadlines given\n\n"
                    "Write in formal but clear and simple legal language."
                )
            },
            {
                "role": "user",
                "content": f"Summarize the following legal document:\n\n{chunk_text}"
            }
        ]



        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        output = model_registry.qa_pipeline(
            prompt,
            max_new_tokens=300,
            temperature=0.2,
            top_p=0.6,
            top_k=10,
            do_sample=False
        )

        generated = output[0]["generated_text"]
        match = re.search(r"<\|assistant\|>(.*)", generated, re.DOTALL)
        summary = match.group(1).strip() if match else generated.strip()

        summaries.append(summary)

    # Step 4: Combine summaries and re-summarize if too long
    combined_summary = " ".join(summaries)
    combined_summary_tokens = tokenizer.encode(combined_summary)

    if len(combined_summary_tokens) > safe_chunk_length:
        # Re-summarize final combined summary
        messages = [
            {"role": "system", "content": (
                "You are a legal assistant summarizing combined legal document summaries. "
                "Produce a final concise and structured summary focusing on: "
                "'From' (who issued the notice), 'To' (whom the notice is addressed to),'Parties Involved', 'Key Legal Issues', 'Main Obligations', and 'Deadlines or Actions Required'."
            )},
            {"role": "user", "content": f"Summarize the following combined summaries:\n\n{combined_summary}"}
        ]

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        output = model_registry.qa_pipeline(
            prompt,
            max_new_tokens=400,
            temperature=0.2,
            top_p=0.6,
            top_k=10,
            do_sample=False
        )

        generated = output[0]["generated_text"]
        match = re.search(r"<\|assistant\|>(.*)", generated, re.DOTALL)
        final_summary = match.group(1).strip() if match else generated.strip()

        return final_summary

    return combined_summary


    """tokenizer = model_registry.summarization_pipeline.tokenizer
    model_max_length = getattr(tokenizer, "model_max_length", 512)
    model_max_length = min(model_max_length, 512)  # Just to be safe


    # Tokenize and split into chunks
    input_tokens = tokenizer.encode(combined_text, truncation=False)
    This ensures:
                    truncation=False avoids dropping extra tokens.
                    Tokens are split into equal-sized safe chunks (≤ 512).
                    ✅ No loss of content.
    

    chunks = [input_tokens[i:i + model_max_length] for i in range(0, len(input_tokens), model_max_length)]

    # Summarize each chunk
    summaries = []
    for chunk in chunks:
        chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
        summary = model_registry.summarization_pipeline(
            chunk_text,
            max_length=250,
            min_length=75,
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
                min_length=175,
                do_sample=False
            )
            final_summaries.append(summary[0]["summary_text"])

        return " ".join(final_summaries)
    
    return final_summary_input"""



def answer_legal_question(query, doc_text):
    """Answers legal questions based on precomputed summary and retrieved legal knowledge using TinyLlama."""
    retrieved_legal_knowledge = retrieve_legal_knowledge(query,limit=1)
    #print("Retrieved legal knowledge:", retrieved_legal_knowledge)

    print("Dcument that user upload :",doc_text)

    # Prepare TinyLlama chat-based prompt
    messages = [
        {"role": "system", "content": "You are a highly skilled legal assistant. If the provided context does not contain sufficient legal information, politely reply: 'I am a legal assistant and cannot assist with non-legal or out-of-domain questions.'Otherwise, provide a clear, well-structured answer organized under the following headings: 'Key Laws', 'Employee Rights', and 'Compliance Requirements'. Provide clear, concise, and complete answers in a structured format. Ensure all sentences are complete and end properly with punctuation. Do not leave answers incomplete."},
        {"role": "user", "content": f"Based on this query: {query}, and context: {retrieved_legal_knowledge}, and user document: {doc_text}, provide a clear and structured legal answer in simple language."}

    ]

    # Generate response using TinyLlama
    prompt = model_registry.qa_pipeline.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = model_registry.qa_pipeline(
        prompt,
        max_new_tokens=100,
        temperature=0.1,     # Lower temperature = more focused output
        top_p=0.6,         # Top-p sampling
        top_k=10,         # Top-k sampling
        do_sample=False
    )

    

    
    # Try to extract only the last assistant message
    generated = outputs[0]["generated_text"]
    match = re.search(r"<\|assistant\|>(.*)", generated, re.DOTALL)
    assistant_response = match.group(1).strip() if match else generated.strip()
    return assistant_response

# Example usage
if __name__ == "__main__":
    pdf_path = "D:/Data_Aces/Codes/ai_legal_assistant/data/user_uploads"  # Replace with your actual PDF path
    #query = "What are the three ways in which a person can be said to abet the doing of a thing under the law of abetment?"
    
    summary = summarize_document(pdf_path)
    print("Summary:", summary)
    
    #answer = answer_legal_question(query, pdf_path)
    #print("Answer:", answer)
