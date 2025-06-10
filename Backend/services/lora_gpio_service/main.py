"""
LoRa GPIO Service GardenConnect
Service pour gérer la communication LoRa via GPIO sur Raspberry Pi
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import time
from shared.config import get_settings
from shared.schemas.common import HealthCheckResponse
from .handlers.lora_handler import LoRaHandler
from .handlers.mqtt_publisher import MQTTPublisher

settings = get_settings()

# Instance globale du handler LoRa
lora_handler = None
mqtt_publisher = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global lora_handler, mqtt_publisher
    
    # Initialisation
    mqtt_publisher = MQTTPublisher()
    await mqtt_publisher.connect()
    
    lora_handler = LoRaHandler(mqtt_publisher)
    await lora_handler.initialize()
    
    # Démarrage de la tâche d'écoute LoRa
    listen_task = asyncio.create_task(lora_handler.start_listening())
    
    yield
    
    # Nettoyage
    listen_task.cancel()
    await lora_handler.cleanup()
    await mqtt_publisher.disconnect()

app = FastAPI(
    title="GardenConnect LoRa GPIO Service",
    version="1.0.0",
    lifespan=lifespan,
    description="Service de communication LoRa via GPIO pour Raspberry Pi"
)

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    lora_status = lora_handler.is_connected() if lora_handler else False
    mqtt_status = mqtt_publisher.is_connected() if mqtt_publisher else False
    
    return HealthCheckResponse(
        status="healthy" if lora_status and mqtt_status else "degraded",
        timestamp=time.time(),
        version="1.0.0",
        service_name="lora-gpio-service",
        database=True,  # Pas de DB directe
        details={
            "lora_connected": lora_status,
            "mqtt_connected": mqtt_status
        }
    )

@app.get("/")
async def root():
    return {"service": "GardenConnect LoRa GPIO Service", "version": "1.0.0"}

@app.post("/send")
async def send_lora_message(message: dict):
    """Envoie un message via LoRa"""
    if not lora_handler:
        return {"error": "LoRa handler not initialized"}
    
    success = await lora_handler.send_message(message)
    return {"success": success, "message": "Message sent" if success else "Failed to send"}

@app.get("/stats")
async def get_stats():
    """Statistiques du service LoRa"""
    if not lora_handler:
        return {"error": "LoRa handler not initialized"}
    
    return await lora_handler.get_stats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)