import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Item
from app.database import get_db, SessionLocal
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="module")
def db():
    db = TestingSessionLocal()
    yield db
    db.close()

def test_create_user(db):
    response = db.execute("INSERT INTO users (username, email) VALUES ('testuser', 'test@example.com') RETURNING id;")
    user_id = response.fetchone()[0]
    db.commit()
    assert user_id is not None

def test_get_user(test_client):
    response = test_client.get("/users/testuser")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_create_item(db):
    response = db.execute("INSERT INTO items (name, description) VALUES ('testitem', 'A test item') RETURNING id;")
    item_id = response.fetchone()[0]
    db.commit()
    assert item_id is not None

def test_get_item(test_client):
    response = test_client.get("/items/testitem")
    assert response.status_code == 200
    assert response.json()["name"] == "testitem"

def test_user_acceptance():
    response = test_client.post("/users/", json={"username": "acceptanceuser", "email": "acceptance@example.com"})
    assert response.status_code == 201
    assert response.json()["username"] == "acceptanceuser"

def test_integration():
    response = test_client.get("/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_error_handling():
    response = test_client.get("/users/nonexistentuser")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

if __name__ == "__main__":
    pytest.main()