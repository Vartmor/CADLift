from fastapi.testclient import TestClient

from app.main import app


def test_register_login_and_refresh_flow():
    with TestClient(app) as client:
        register_payload = {
            "email": "test@example.com",
            "password": "SuperSecret123",
            "display_name": "Test User",
        }
        response = client.post("/api/v1/auth/register", json=register_payload)
        assert response.status_code == 200
        tokens = response.json()
        assert tokens["access_token"]
        assert tokens["refresh_token"]

        login_payload = {
            "email": "test@example.com",
            "password": "SuperSecret123",
        }
        response = client.post("/api/v1/auth/login", json=login_payload)
        assert response.status_code == 200
        login_tokens = response.json()
        assert login_tokens["access_token"]

        refresh_payload = {"refresh_token": login_tokens["refresh_token"]}
        response = client.post("/api/v1/auth/refresh", json=refresh_payload)
        assert response.status_code == 200
        refreshed_tokens = response.json()
        assert refreshed_tokens["access_token"] != login_tokens["access_token"]
