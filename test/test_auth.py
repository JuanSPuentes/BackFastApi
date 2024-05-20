import pytest
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from database import engine
from main import app, get_db
from models.user_model import CreateUserRequest

client = TestClient(app)

def test_create_user_with_valid_username():
    response = client.post(
        "/auth/",
        json={"username": "testuser@gmail.com", "password": "testpassword"},
    )
    assert response.status_code == 201
    assert response.json() == {"username": "testuser@gmail.com"}

def test_create_user_with_invalid_username():
    response = client.post(
        "/auth/",
        json={"username": "test", "password": "testpassword"},
    )
    assert response.status_code == 422
    
def test_create_user_request_with_invalid_password():
    with pytest.raises(ValueError):
        CreateUserRequest(username="testuser@gmail.com", password="short")

def test_create_user_request_with_empty_password():
    with pytest.raises(ValueError):
        CreateUserRequest(username="testuser@gmail.com", password="")

def test_create_user_request_with_long_password():
    request = CreateUserRequest(username="testuser@gmail.com", password="averylongpassword")
    assert request.username == "testuser@gmail.com"
    assert request.password == "averylongpassword"

def test_login_for_access_token():
    response = client.post(
        "/auth/token",
        data={"username": "testuser@gmail.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_user_endpoint_with_valid_user():
    token = client.post(
        "/auth/token",
        data={"username": "testuser@gmail.com", "password": "testpassword"},
    ).json()["access_token"]

    response = client.get("/", headers={"Authorization": 'Bearer ' + token})
    assert response.status_code == 200
    assert response.json()['data']['User']['username'] ==  "testuser@gmail.com"

def test_user_endpoint_with_invalid_user():
    response = client.get("/", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}