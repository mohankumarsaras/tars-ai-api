from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_intelligence_engine():
    # Insert profile to ensure user_id 1 exists
    profile_data = {"id": 1, "first_name": "Test", "last_name": "User", "email": "test@test.com"}
    try:
        client.post("/api/v1/profile/", json=profile_data)
    except Exception:
        pass
        
    response = client.post("/api/v1/intelligence/analyze/1")
    assert response.status_code == 200
    data = response.json()
    assert "strengths" in data
    assert "career_risks" in data
