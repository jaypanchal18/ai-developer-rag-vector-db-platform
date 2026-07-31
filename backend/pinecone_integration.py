import os
import pinecone
from fastapi import HTTPException

class PineconeIntegration:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT")
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        self.index = None
        self.initialize_pinecone()

    def initialize_pinecone(self):
        try:
            pinecone.init(api_key=self.api_key, environment=self.environment)
            if self.index_name not in pinecone.list_indexes():
                pinecone.create_index(self.index_name, dimension=768)  # Adjust dimension as needed
            self.index = pinecone.Index(self.index_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize Pinecone: {str(e)}")

    def upsert_vectors(self, vectors):
        try:
            self.index.upsert(vectors)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upsert vectors: {str(e)}")

    def query_vectors(self, vector, top_k=5):
        try:
            results = self.index.query(vector, top_k=top_k)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to query vectors: {str(e)}")

    def delete_vector(self, vector_id):
        try:
            self.index.delete(ids=[vector_id])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete vector: {str(e)}")

pinecone_integration = PineconeIntegration()