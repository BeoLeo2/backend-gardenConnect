"""Tests pour auth_service"""
def test_auth_service_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service_name"] == "auth-service"

def test_auth_service_root(client):
    response = client.get("/")
    assert response.status_code == 200
