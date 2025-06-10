"""Tests pour data_service"""
def test_data_service_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service_name"] == "data-service"

def test_data_service_root(client):
    response = client.get("/")
    assert response.status_code == 200
