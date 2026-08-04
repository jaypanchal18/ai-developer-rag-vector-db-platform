from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pinecone
import tensorflow as tf
import os

DATABASE_URL = os.getenv("DATABASE_URL")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)

class DocumentCreate(BaseModel):
    title: str
    content: str

class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str

app = FastAPI()

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/documents/", response_model=DocumentResponse)
def create_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    db_doc = Document(title=doc.title, content=doc.content)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # Indexing the document in Pinecone
    try:
        embedding = tf.keras.preprocessing.text.text_to_word_sequence(doc.content)
        pinecone_index = pinecone.Index("documents")
        pinecone_index.upsert([(str(db_doc.id), embedding)])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing document: {str(e)}")
    
    return db_doc

@app.get("/documents/{doc_id}", response_model=DocumentResponse)
def read_document(doc_id: int, db: Session = Depends(get_db)):
    db_doc = db.query(Document).filter(Document.id == doc_id).first()
    if db_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc

@app.get("/documents/")
def read_documents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    documents = db.query(Document).offset(skip).limit(limit).all()
    return documents

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Implement authentication logic here
    pass

@app.get("/")
def read_root():
    return {"Hello": "World"}