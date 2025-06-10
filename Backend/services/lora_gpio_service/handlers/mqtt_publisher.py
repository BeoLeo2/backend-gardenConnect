"""
Publisher MQTT pour le service LoRa GPIO
Publie les données reçues via LoRa vers les autres services
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional
import aiomqtt
from shared.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class MQTTPublisher:
    def __init__(self):
        self.client: Optional[aiomqtt.Client] = None
        self.is_connected_flag = False
        
    async def connect(self):
        """Connexion au broker MQTT"""
        try:
            self.client = aiomqtt.Client(
                hostname=getattr(settings, 'MQTT_HOST', 'localhost'),
                port=getattr(settings, 'MQTT_PORT', 1883),
                username=getattr(settings, 'MQTT_USERNAME', None),
                password=getattr(settings, 'MQTT_PASSWORD', None),
                client_id="lora_gpio_service"
            )
            
            await self.client.__aenter__()
            self.is_connected_flag = True
            logger.info("Connected to MQTT broker")
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            self.is_connected_flag = False
            raise
    
    def is_connected(self) -> bool:
        """Vérifie la connexion MQTT"""
        return self.is_connected_flag and self.client is not None
    
    async def publish(self, topic: str, message: Dict[str, Any]):
        """Publie un message sur un topic MQTT"""
        if not self.is_connected():
            raise RuntimeError("MQTT client not connected")
        
        try:
            message_json = json.dumps(message, default=str)
            await self.client.publish(topic, message_json, qos=1)
            logger.debug(f"Published to {topic}: {message.get('type', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            raise
    
    async def publish_sensor_data(self, node_id: str, sensor_data: Dict[str, Any]):
        """Publie des données de capteur"""
        topic = f"gardenconnect/nodes/{node_id}/data"
        await self.publish(topic, {
            "type": "sensor_data",
            "node_id": node_id,
            "data": sensor_data,
            "timestamp": sensor_data.get("timestamp")
        })
    
    async def publish_node_status(self, node_id: str, status: str, details: Dict[str, Any] = None):
        """Publie le statut d'un nœud"""
        topic = f"gardenconnect/nodes/{node_id}/status"
        await self.publish(topic, {
            "type": "node_status",
            "node_id": node_id,
            "status": status,
            "details": details or {}
        })
    
    async def publish_alert(self, node_id: str, alert_type: str, message: str, severity: str = "warning"):
        """Publie une alerte"""
        topic = f"gardenconnect/nodes/{node_id}/alert"
        await self.publish(topic, {
            "type": "alert",
            "node_id": node_id,
            "alert_type": alert_type,
            "message": message,
            "severity": severity
        })
    
    async def disconnect(self):
        """Déconnexion du broker MQTT"""
        try:
            if self.client:
                await self.client.__aexit__(None, None, None)
                self.is_connected_flag = False
                logger.info("Disconnected from MQTT broker")
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT: {e}")
            self.is_connected_flag = False