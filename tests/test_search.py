from fastapi.testclient import TestClient
from app.main import app
from app.database.database import get_db, engine, Base
import pytest

client = TestClient(app)

def test_search_provider_indexing():
    # Create knowledge record
    record_data = {
        "user_id": 1,
        "title": "Machine Learning",
        "content": "A subset of AI focused on learning from data without explicit programming.",
        "category": "concept",
        "source": "Textbook",
        "verification_status": "VERIFIED"
    }
    
    response = client.post("/api/v1/knowledge/", json=record_data)
    assert response.status_code == 200
    
    # Search for it
    search_resp = client.get("/api/v1/search/?query=Machine")
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) > 0
    assert results[0]["result"] == "Machine Learning"
    assert results[0]["category"] == "Knowledge"
