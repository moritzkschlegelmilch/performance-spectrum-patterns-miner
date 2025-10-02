from fastapi.testclient import TestClient
import sys
import os

# Allow imports from app/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from main import app
from database import Base, get_db

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use a separate test DB
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Override FastAPI's DB dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create tables for tests
Base.metadata.create_all(bind=engine)

client = TestClient(app)