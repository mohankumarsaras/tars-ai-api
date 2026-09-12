from fastapi.testclient import TestClient
from app.main import app
from app.database.database import get_db, engine, Base
import pytest
from app import models

client = TestClient(app)

def test_skill_evaluation():
    # Insert a dummy user, category, and skill if not present
    profile_data = {"id": 1, "name": "Test User", "email": "test@test.com"}
    try:
        client.post("/api/v1/profile/", json=profile_data)
    except Exception:
        pass
        
    cat_data = {"user_id": 1, "name": "Cloud"}
    cat_resp = client.post("/api/v1/skills/categories", json=cat_data)
    if cat_resp.status_code == 200:
        cat_id = cat_resp.json()["id"]
    else:
        cat_id = 1
        
    skill_data = {"category_id": cat_id, "name": "AWS VPC", "familiarity": "expert"}
    skill_resp = client.post("/api/v1/skills/", json=skill_data)
    if skill_resp.status_code == 200:
        skill_id = skill_resp.json()["id"]
    else:
        skill_id = 1

    # Add evidence 
    ev_data1 = {"user_id": 1, "description": "AWS VPC Certification", "source_type": "Certification"}
    ev_data2 = {"user_id": 1, "description": "AWS VPC project deployment", "source_type": "Project"}
    client.post("/api/v1/evidence/", json=ev_data1)
    client.post("/api/v1/evidence/", json=ev_data2)
    
    # Trigger evaluation
    eval_resp = client.post(f"/api/v1/skills/{skill_id}/evaluate")
    assert eval_resp.status_code == 200
    
    data = eval_resp.json()
    assert "overall_score" in data
    assert "confidence_level" in data
    # 2 diverse sources -> Moderate
    assert "Moderate" in data["confidence_level"]
