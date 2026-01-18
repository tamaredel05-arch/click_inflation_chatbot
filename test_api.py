from fastapi.testclient import TestClient
from api import app

def test_chat_endpoint():
    client = TestClient(app)
    response = client.post("/chat", json={"message": "Hello from test"})
    print("Status code:", response.status_code)
    print("Response JSON:", response.json())
    assert response.status_code == 200
    assert "response" in response.json()
    assert isinstance(response.json()["response"], str)

def test_cors_headers():
    client = TestClient(app)
    response = client.options("/chat", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    })
    print("CORS headers:", response.headers)
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert "access-control-allow-methods" in response.headers
