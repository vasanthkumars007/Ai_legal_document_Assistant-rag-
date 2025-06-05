# 🧾 AI-Powered Legal Document Assistant using SLM and Qdrant

The AI Legal Document Assistant is an intelligent system designed to summarize and explain legal documents using Small Language Models (SLMs) and vector similarity search. When a user uploads a legal PDF, the document is parsed and broken into overlapping chunks. These chunks are embedded into high-dimensional vectors and stored in a Qdrant vector database.

During summarization, the system retrieves relevant legal context from Qdrant based on semantic similarity, then combines it with the uploaded document text. The summarization model uses this contextualized input to generate a clear, structured summary.

When a user asks a follow-up question about the uploaded document, the system again queries Qdrant to find the most relevant legal knowledge. The retrieved context, along with the user's question and the document summary, is passed to the TinyLlama SLM to generate an accurate and easy-to-understand legal response.

---



## 🚀 Features

- 🔍 Summarize uploaded legal documents
- 🤖 Answer user legal questions contextually
- 💾 Uses Qdrant vector DB for fast semantic retrieval
- 🧠 Powered by TinyLlama & SentenceTransformers (SLM may change Accordingly to specific usage)
- 📦 FastAPI backend + React frontend (optional)

## 🛠️ Tech Stack

| Layer        | Tech                                 |
|--------------|--------------------------------------|
| Backend      | Python, FastAPI                      |
| AI Models    | TinyLlama, BART, SentenceTransformers|
| Vector Store | Qdrant                               |
| Embeddings   | all-MiniLM-L6-v2                     |
| Frontend     | React (with or without Tailwind)     |
| Parsing      | pdfplumber                           |

---
## ⚙️ How It Works

1. Legal PDFs (Doc 1) are chunked and embedded
2. Stored in Qdrant (vector DB)
3. Users upload documents (Doc 2)
4. System summarizes them
5. Users ask legal questions → retrieved context → passed to TinyLlama
6. Model answers with legal clarity

---

## 🧰 Setup Instructions

```bash
# 1. Clone the repo
git clone https://github.com/your-username/ai-legal-assistant
cd ai-legal-assistant

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Qdrant via Docker
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant

# 5. Launch FastAPI
python main.py


This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


