from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import psycopg2
import pinecone
import numpy as np
import tensorflow as tf

app = FastAPI()

# Database connection parameters
DB_HOST = "your_db_host"
DB_NAME = "your_db_name"
DB_USER = "your_db_user"
DB_PASS = "your_db_password"

# Pinecone initialization
PINECONE_API_KEY = "your_pinecone_api_key"
pinecone.init(api_key=PINECONE_API_KEY, environment="us-west1-gcp")

# Define the model for search input
class SearchRequest(BaseModel):
    query: str
    top_k: int = 10

# Function to connect to PostgreSQL
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

# Function to perform keyword search in PostgreSQL
def keyword_search(query: str, top_k: int) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM documents WHERE content ILIKE %s LIMIT %s", (f"%{query}%", top_k))
        results = cursor.fetchall()
        return [{"id": row[0], "content": row[1]} for row in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword search error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Function to perform vector search using Pinecone
def vector_search(query: str, top_k: int) -> List[dict]:
    # Convert query to vector using a pre-trained TensorFlow model
    model = tf.keras.models.load_model("path_to_your_model")
    query_vector = model.predict(np.array([query]))  # Assuming the model takes a string input
    query_vector = query_vector.tolist()

    index = pinecone.Index("your_index_name")
    results = index.query(queries=query_vector, top_k=top_k)
    return [{"id": match.id, "score": match.score} for match in results.matches]

# Hybrid search endpoint
@app.post("/hybrid_search", response_model=List[dict])
async def hybrid_search(request: SearchRequest):
    try:
        keyword_results = keyword_search(request.query, request.top_k)
        vector_results = vector_search(request.query, request.top_k)

        # Combine results (simple merge, can be improved with ranking logic)
        combined_results = keyword_results + vector_results
        return combined_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hybrid search error: {str(e)}")