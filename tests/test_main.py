from fastapi.testclient import TestClient
from app.main import app
from app.database.database import engine

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "application": "TARS"}

def test_startup_event():
    # Simple test for startup logic if needed
    assert app.title == "TARS API"

def test_database_connection():
    # Attempt to connect to the database
    try:
        connection = engine.connect()
        connection.close()
        connected = True
    except Exception:
        connected = False
    assert connected is True
