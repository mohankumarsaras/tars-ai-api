from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_pipeline():
    # Since we are using the mock key "sk-mock" by default in config, this won't hit the internet
    response = client.post("/api/v1/chat/ask", json={"question": "What is my career history?"})
    assert response.status_code == 200
    
    data = response.json()
    assert "FACTS:" in data["response"]
    assert "EVIDENCE:" in data["response"]
    assert "ANALYSIS:" in data["response"]
    assert "OPINION:" in data["response"]
    assert "RECOMMENDATION:" in data["response"]
