# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db
from models.user_model import User

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def token(client, db_session):
    client.post("/auth/", json={"username": "admin@example.com", "password": "adminpassword"})
    db_session.query(User).where(User.username == "admin@example.com").update({User.user_type: 'admin'})
    db_session.commit()
    token = client.post(
        "/auth/token",
        data={"username": "admin@example.com", "password": "adminpassword"},
    ).json()["access_token"]
    db_session.close()
    return token
