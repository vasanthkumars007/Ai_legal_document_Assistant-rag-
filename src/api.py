from fastapi import FastAPI, File, UploadFile, Form
import os
from embedding_store import store_legal_knowledge
from model import summarize_document, answer_legal_question

app = FastAPI()

@app.post("/store_legal_knowledge/")
async def store_knowledge():
    return store_legal_knowledge()

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"D:/Data_Aces/Codes/ai_legal_assistant/data/user_uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    summary = summarize_document(file_path)
    return {"summary": summary}

@app.get("/ask/")
async def ask_question(query: str = Form(...), file_name: str = Form(...)):
    file_path = f"D:/Data_Aces/Codes/ai_legal_assistant/data/user_uploads/{file_name}"
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    answer = answer_legal_question(query, file_path)
    return {"answer": answer}
