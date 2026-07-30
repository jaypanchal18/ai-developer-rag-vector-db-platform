import os
import json
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pinecone import PineconeClient

app = FastAPI()
pinecone_client = PineconeClient(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = pinecone_client.Index("document-embeddings")

class Document(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    id: str
    embedding: List[float]

# Load pre-trained TensorFlow model
model = tf.keras.models.load_model(os.getenv("MODEL_PATH"))

def create_embedding(text: str) -> List[float]:
    try:
        # Preprocess the text for the model
        input_data = tf.convert_to_tensor([text])
        embedding = model.predict(input_data)
        return embedding[0].tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating embedding: {str(e)}")

@app.post("/embed", response_model=EmbeddingResponse)
async def embed_document(document: Document):
    try:
        embedding = create_embedding(document.text)
        # Generate a unique ID for the document
        doc_id = str(np.random.randint(1e6))
        # Upsert the embedding into Pinecone
        pinecone_index.upsert([(doc_id, embedding)])
        return EmbeddingResponse(id=doc_id, embedding=embedding)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")