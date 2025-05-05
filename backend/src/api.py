from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from .embedding_store import store_legal_knowledge
from .model import model_registry, summarize_document, answer_legal_question




#  Store the latest document summary for reuse in legal_chat
latest_summary = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(" Loading models at startup...")
    model_registry.load_models()
    yield  # <-- this is where the app runs
    print(" Shutting down... ")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return { "Welcome to the Ai legal Assistant API"}

@app.post("/store_legal_knowledge/")
async def store_knowledge():
    return store_legal_knowledge()

@app.post("/summary/")
async def upload_pdf(file: UploadFile = File(...)):
    global latest_summary

    file_path = f"D:/Data_Aces/Codes/ai_legal_assistant/backend/data/user_uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    summary = summarize_document(file_path)
    latest_summary = summary  # <-- Store for later use
    global doc_text
    return {"summary": summary}


@app.post("/legal_chat/")
async def ask_question(query: str = Form(...)):
    global doc_text

    if latest_summary is None:
        return {"error": "No document has been summarized yet."}

    answer = answer_legal_question(query, latest_summary)
    return {"answer": answer}

