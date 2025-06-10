"""
Routes pour MQTT
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def get_mqtt_status():
    """Récupérer le statut MQTT"""
    return {"status": "connected"}

@router.post("/publish")
async def publish_message():
    """Publier un message MQTT"""
    return {"message": "Message published"}