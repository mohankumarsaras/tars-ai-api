from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_assessment_engine():
    # Insert profile to ensure user_id 1 exists
    profile_data = {"id": 1, "first_name": "Test", "last_name": "User", "email": "test@test.com"}
    try:
        client.post("/api/v1/profile/", json=profile_data)
    except Exception:
        pass
        
    cat_data = {"user_id": 1, "name": "Cloud"}
    cat_resp = client.post("/api/v1/skills/categories", json=cat_data)
    cat_id = cat_resp.json().get("id", 1)
        
    skill_data = {"category_id": cat_id, "name": "AWS VPC", "familiarity": "expert"}
    skill_resp = client.post("/api/v1/skills/", json=skill_data)
    skill_id = skill_resp.json().get("id", 1)

    # Generate assessment
    gen_resp = client.post("/api/v1/assessments/generate", json={
        "skill_id": skill_id,
        "assessment_type": "Technical explanation"
    })
    assert gen_resp.status_code == 200
    data = gen_resp.json()
    assert "content" in data
    assessment_id = data["id"]
    
    # Submit attempt
    sub_resp = client.post(f"/api/v1/assessments/{assessment_id}/submit", json={
        "user_id": 1,
        "user_responses": "[{'id': 1, 'answer': 'VPC is a virtual network.'}]"
    })
    assert sub_resp.status_code == 200
    sub_data = sub_resp.json()
    assert "score" in sub_data
