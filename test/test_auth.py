import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, StaticPool
from fastapi.testclient import TestClient
from database import SessionLocal, engine
from models.models import User, UserType
from main import app, get_db

client = TestClient(app)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db

def test_create_user():
    response = client.post(
        "/auth/",
        json={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 201
    assert response.json() == {"username": "testuser"}
    
def test_login_for_access_token():
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_user_endpoint_with_valid_user():
    token = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"},
    ).json()["access_token"]

    response = client.get("/", headers={"Authorization": 'Bearer ' + token})
    assert response.status_code == 200
    assert response.json()['user']['username'] ==  "testuser"

def test_user_endpoint_with_invalid_user():
    response = client.get("/", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}