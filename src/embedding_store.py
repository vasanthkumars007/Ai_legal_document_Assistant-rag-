from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from pdf_processing import extract_text_from_all_pdfs
import os
import config  # Import the config file

# Initialize Qdrant
qdrant = QdrantClient(url=config.QDRANT_URL, timeout=60.0)  # Use QDRANT_URL from config
embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)  # Use EMBEDDING_MODEL from config

# Check if the collection exists, and create it if it doesn't
if not qdrant.collection_exists(collection_name=config.COLLECTION_NAME):
    qdrant.create_collection(
        collection_name=config.COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

def store_legal_knowledge():
    """Extracts text from legal knowledge PDFs and stores in Qdrant."""
    folder_path = "D:/Data_Aces/Codes/ai_legal_assistant/data/legal_knowledge/"
    all_texts = extract_text_from_all_pdfs(folder_path)
    for filename, text in all_texts.items():
        sentences = text.split("\n")
        vectors = embedding_model.encode(sentences)

        points = [
            PointStruct(id=i, vector=vectors[i].tolist(), payload={"text": sentences[i]})
            for i in range(len(sentences))
        ]

        """1 vector ≈ 3KB
           1000 vectors ≈ 3MB
           Qdrant limit = 32MB
           Thus, 10,000 vectors could exceed the limit and fail, whereas 1000 keeps it safe."""

        BATCH_SIZE = 1000  # Adjust the batch size as needed (allowed by Qdrant is 32 mb per batch)
        # Upsert points in batches to Qdrant
        for i in range(0, len(points), BATCH_SIZE):
            batch = points[i:i + BATCH_SIZE]
            qdrant.upsert(collection_name=config.COLLECTION_NAME, points=batch)

    return {"status": "Legal knowledge stored successfully!"}

# Example usage
if __name__ == "__main__":
    result = store_legal_knowledge()
    print(result)
