import pytest
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.services.import_service import ImportService
from app import models

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_seed_file(tmp_path):
    data = {
        "profile": {
            "display_name": "Test User",
            "professional_identity": "Test Engineer"
        },
        "education": [
            {
                "qualification": "B.Tech",
                "institution": "Test College",
                "result": "8.0",
                "source": "resume"
            }
        ],
        "career": [
            {
                "role": "Engineer",
                "organization": "Test Corp",
                "period": "2020 - 2022",
                "domain": "Tech",
                "evidence": ["Did some testing"],
                "source": "resume",
                "confidence": "high"
            }
        ],
        "skills_documented": ["Python", "Testing"],
        "certifications_mentioned": [
            {
                "name": "Test Cert",
                "code": "TC-01",
                "verification": "needs_verification"
            }
        ]
    }
    file_path = tmp_path / "test_seed.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return str(file_path)

def test_import_success(db_session, mock_seed_file):
    service = ImportService(db_session)
    stats = service.process_import(mock_seed_file)
    
    assert stats["status"] == "SUCCESS"
    assert stats["categories"]["profile"] == 1
    assert stats["categories"]["education"] == 1
    assert stats["categories"]["career"] == 1
    assert stats["categories"]["evidence"] == 1
    assert stats["categories"]["skills"] == 2
    assert stats["categories"]["certifications"] == 1
    
    # Verify skill score is null
    skill = db_session.query(models.Skill).filter_by(name="Python").first()
    assert skill is not None
    assert skill.score is None
    assert skill.assessment_status == "NOT_ASSESSED"

def test_import_idempotency(db_session, mock_seed_file):
    service = ImportService(db_session)
    stats1 = service.process_import(mock_seed_file)
    assert stats1["status"] == "SUCCESS"
    assert stats1["records_created"] > 0
    
    stats2 = service.process_import(mock_seed_file)
    assert stats2["status"] == "SUCCESS"
    assert stats2["duplicates"] == 1
    assert stats2["records_created"] == 0

def test_malformed_json(db_session, tmp_path):
    file_path = tmp_path / "bad.json"
    with open(file_path, "w") as f:
        f.write("{ bad json }")
        
    service = ImportService(db_session)
    stats = service.process_import(str(file_path))
    assert stats["status"] == "FAILED"
    assert stats["validation_errors"] == 1
