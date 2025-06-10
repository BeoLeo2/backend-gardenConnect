"""
Handler pour la communication LoRa via GPIO
Gère l'interface avec le module SX1278 sur Raspberry Pi
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from ..drivers.sx1278_driver import SX1278Driver
from .mqtt_publisher import MQTTPublisher

logger = logging.getLogger(__name__)

class LoRaHandler:
    def __init__(self, mqtt_publisher: MQTTPublisher):
        self.mqtt_publisher = mqtt_publisher
        self.sx1278_driver = None
        self.is_listening = False
        self.stats = {
            "messages_received": 0,
            "messages_sent": 0,
            "errors": 0,
            "last_message_time": None,
            "start_time": datetime.now()
        }
    
    async def initialize(self):
        """Initialise le driver LoRa"""
        try:
            self.sx1278_driver = SX1278Driver()
            await self.sx1278_driver.initialize()
            logger.info("LoRa handler initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LoRa handler: {e}")
            self.stats["errors"] += 1
            return False
    
    def is_connected(self) -> bool:
        """Vérifie si le module LoRa est connecté"""
        return self.sx1278_driver is not None and self.sx1278_driver.is_ready()
    
    async def start_listening(self):
        """Démarre l'écoute des messages LoRa"""
        if not self.is_connected():
            logger.error("Cannot start listening: LoRa not connected")
            return
        
        self.is_listening = True
        logger.info("Starting LoRa listening loop")
        
        try:
            while self.is_listening:
                try:
                    # Écoute non-bloquante avec timeout
                    message = await self.sx1278_driver.receive_message(timeout=1.0)
                    
                    if message:
                        await self._handle_received_message(message)
                    
                    # Petit délai pour éviter la surcharge CPU
                    await asyncio.sleep(0.1)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in listening loop: {e}")
                    self.stats["errors"] += 1
                    await asyncio.sleep(1.0)  # Délai plus long en cas d'erreur
                    
        except asyncio.CancelledError:
            logger.info("LoRa listening loop cancelled")
        finally:
            self.is_listening = False
    
    async def _handle_received_message(self, raw_message: bytes):
        """Traite un message LoRa reçu"""
        try:
            # Tentative de décodage JSON
            message_str = raw_message.decode('utf-8')
            message_data = json.loads(message_str)
            
            # Ajout de métadonnées
            enriched_message = {
                **message_data,
                "received_at": datetime.now().isoformat(),
                "rssi": await self.sx1278_driver.get_rssi(),
                "snr": await self.sx1278_driver.get_snr()
            }
            
            # Publication MQTT selon le type de message
            await self._publish_to_mqtt(enriched_message)
            
            self.stats["messages_received"] += 1
            self.stats["last_message_time"] = datetime.now()
            
            logger.info(f"Processed LoRa message: {message_data.get('type', 'unknown')}")
            
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in LoRa message: {raw_message}")
            self.stats["errors"] += 1
        except Exception as e:
            logger.error(f"Error handling LoRa message: {e}")
            self.stats["errors"] += 1
    
    async def _publish_to_mqtt(self, message: Dict[str, Any]):
        """Publie le message sur MQTT selon son type"""
        message_type = message.get("type", "unknown")
        node_id = message.get("node_id", "unknown")
        
        # Topics MQTT selon le type de message
        topic_mapping = {
            "sensor_data": f"gardenconnect/nodes/{node_id}/data",
            "heartbeat": f"gardenconnect/nodes/{node_id}/heartbeat",
            "alert": f"gardenconnect/nodes/{node_id}/alert",
            "status": f"gardenconnect/nodes/{node_id}/status",
            "unknown": f"gardenconnect/nodes/{node_id}/raw"
        }
        
        topic = topic_mapping.get(message_type, topic_mapping["unknown"])
        
        try:
            await self.mqtt_publisher.publish(topic, message)
            logger.debug(f"Published to MQTT topic: {topic}")
        except Exception as e:
            logger.error(f"Failed to publish to MQTT: {e}")
            self.stats["errors"] += 1
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Envoie un message via LoRa"""
        if not self.is_connected():
            logger.error("Cannot send message: LoRa not connected")
            return False
        
        try:
            # Ajout de métadonnées
            enriched_message = {
                **message,
                "sent_at": datetime.now().isoformat(),
                "gateway_id": "raspi_gateway"
            }
            
            # Encodage JSON
            message_json = json.dumps(enriched_message)
            message_bytes = message_json.encode('utf-8')
            
            # Envoi via LoRa
            success = await self.sx1278_driver.send_message(message_bytes)
            
            if success:
                self.stats["messages_sent"] += 1
                logger.info(f"LoRa message sent: {message.get('type', 'unknown')}")
            else:
                self.stats["errors"] += 1
                logger.error("Failed to send LoRa message")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending LoRa message: {e}")
            self.stats["errors"] += 1
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du handler"""
        return {
            **self.stats,
            "is_listening": self.is_listening,
            "is_connected": self.is_connected(),
            "uptime_seconds": (datetime.now() - self.stats["start_time"]).total_seconds()
        }
    
    async def cleanup(self):
        """Nettoie les ressources"""
        self.is_listening = False
        
        if self.sx1278_driver:
            await self.sx1278_driver.cleanup()
            
        logger.info("LoRa handler cleaned up")