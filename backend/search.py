from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pinecone
import tensorflow as tf
import numpy as np
import os

# Initialize Pinecone
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))

# Create a FastAPI router
router = APIRouter()

# Define the request model
class SearchRequest(BaseModel):
    query: str

# Define the response model
class SearchResponse(BaseModel):
    results: list

# Load your TensorFlow model for embedding
model = tf.keras.models.load_model(os.getenv("MODEL_PATH"))

def embed_query(query: str) -> np.ndarray:
    # Preprocess the query and generate embeddings
    processed_query = tf.keras.preprocessing.text.text_to_word_sequence(query)
    embeddings = model.predict(np.array([processed_query]))
    return embeddings

@router.post("/search", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    try:
        # Generate embeddings for the query
        query_embedding = embed_query(request.query)

        # Query Pinecone for similar vectors
        index = pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))
        response = index.query(queries=query_embedding.tolist(), top_k=10)

        # Extract results
        results = [{"id": match.id, "score": match.score} for match in response.matches]

        return SearchResponse(results=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))