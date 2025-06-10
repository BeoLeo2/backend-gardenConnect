"""Tests pour alert_service"""
def test_alert_service_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service_name"] == "alert-service"

def test_alert_service_root(client):
    response = client.get("/")
    assert response.status_code == 200
