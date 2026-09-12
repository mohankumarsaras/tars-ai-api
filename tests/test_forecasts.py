from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_forecasting_engine():
    # Insert profile to ensure user_id 1 exists
    profile_data = {"id": 1, "first_name": "Test", "last_name": "User", "email": "test@test.com"}
    try:
        client.post("/api/v1/profile/", json=profile_data)
    except Exception:
        pass
        
    sim_resp = client.post("/api/v1/forecasts/simulate", json={
        "user_id": 1,
        "query": "What if I focus on Kubernetes?"
    })
    
    assert sim_resp.status_code == 200
    data = sim_resp.json()
    assert "query" in data
    assert "paths" in data
    assert len(data["paths"]) > 0
