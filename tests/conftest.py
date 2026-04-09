import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_activity():
    """Provide a sample activity name for testing"""
    return "Chess Club"


@pytest.fixture
def sample_email():
    """Provide a sample email for testing"""
    return "test@mergington.edu"
