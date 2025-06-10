"""Tests pour mqtt_service"""
def test_mqtt_service_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service_name"] == "mqtt-service"

def test_mqtt_service_root(client):
    response = client.get("/")
    assert response.status_code == 200
