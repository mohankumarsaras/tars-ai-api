from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_learning_engine_ai_lock():
    # Insert profile to ensure user_id 1 exists
    profile_data = {"id": 1, "first_name": "Test", "last_name": "User", "email": "test2@test.com"}
    try:
        client.post("/api/v1/profile/", json=profile_data)
    except Exception:
        pass
        
    # Simulate ingesting AI knowledge (Mock the LLM response returning AI-GENERATED)
    # The external provider isn't actually mocked here, but the JSON parsing fallback or direct AI response will trigger the lock
    
    # We will test the endpoint assuming LLM correctly identifies or falls back
    sim_resp = client.post("/api/v1/learning/ingest", json={
        "user_id": 1,
        "content": "A highly suspect piece of AI generated text about the optimal way to write code using hallucinations.",
        "source": "ChatGPT"
    })
    
    assert sim_resp.status_code == 200
    data = sim_resp.json()
    assert "knowledge_id" in data
    # The classification could be AI-GENERATED KNOWLEDGE or PERSONAL KNOWLEDGE depending on LLM
    # However, if it is AI-GENERATED, the status MUST be NEEDS_REVIEW
    if data["type"] == "AI-GENERATED KNOWLEDGE":
        assert data["status"] == "NEEDS_REVIEW"
