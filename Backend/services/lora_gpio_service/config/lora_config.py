"""
Configuration spécifique au service LoRa GPIO
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class LoRaGPIOConfig:
    """Configuration pour le service LoRa GPIO"""
    
    # Configuration matérielle
    spi_bus: int = 0
    spi_device: int = 0
    reset_pin: int = 22
    dio0_pin: int = 18
    dio1_pin: int = 23
    
    # Paramètres LoRa
    frequency: int = 868000000  # 868 MHz (Europe)
    tx_power: int = 14  # dBm
    spreading_factor: int = 7
    bandwidth: int = 125000  # 125 kHz
    coding_rate: int = 5  # 4/5
    preamble_length: int = 8
    sync_word: int = 0x12
    
    # Configuration réseau
    gateway_id: str = "raspi_gateway_01"
    network_id: int = 1
    
    # Timeouts et intervalles
    rx_timeout: float = 1.0  # secondes
    tx_timeout: float = 5.0  # secondes
    heartbeat_interval: int = 30  # secondes
    
    # Configuration MQTT
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_keepalive: int = 60
    mqtt_qos: int = 1
    
    # Topics MQTT
    mqtt_topics: Dict[str, str] = None
    
    def __post_init__(self):
        if self.mqtt_topics is None:
            self.mqtt_topics = {
                "sensor_data": "gardenconnect/nodes/{node_id}/data",
                "heartbeat": "gardenconnect/nodes/{node_id}/heartbeat",
                "alert": "gardenconnect/nodes/{node_id}/alert",
                "status": "gardenconnect/nodes/{node_id}/status",
                "command": "gardenconnect/nodes/{node_id}/command",
                "gateway_status": f"gardenconnect/gateway/{self.gateway_id}/status"
            }
    
    def get_node_topic(self, topic_type: str, node_id: str) -> str:
        """Génère un topic MQTT pour un nœud spécifique"""
        template = self.mqtt_topics.get(topic_type, "gardenconnect/unknown")
        return template.format(node_id=node_id, gateway_id=self.gateway_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire"""
        return {
            "hardware": {
                "spi_bus": self.spi_bus,
                "spi_device": self.spi_device,
                "reset_pin": self.reset_pin,
                "dio0_pin": self.dio0_pin,
                "dio1_pin": self.dio1_pin
            },
            "lora": {
                "frequency": self.frequency,
                "tx_power": self.tx_power,
                "spreading_factor": self.spreading_factor,
                "bandwidth": self.bandwidth,
                "coding_rate": self.coding_rate,
                "preamble_length": self.preamble_length,
                "sync_word": self.sync_word
            },
            "network": {
                "gateway_id": self.gateway_id,
                "network_id": self.network_id
            },
            "timeouts": {
                "rx_timeout": self.rx_timeout,
                "tx_timeout": self.tx_timeout,
                "heartbeat_interval": self.heartbeat_interval
            },
            "mqtt": {
                "host": self.mqtt_host,
                "port": self.mqtt_port,
                "keepalive": self.mqtt_keepalive,
                "qos": self.mqtt_qos,
                "topics": self.mqtt_topics
            }
        }

# Configuration par défaut
DEFAULT_LORA_CONFIG = LoRaGPIOConfig()

# Configurations prédéfinies pour différents environnements
CONFIGS = {
    "development": LoRaGPIOConfig(
        frequency=433000000,  # 433 MHz pour les tests
        tx_power=10,
        mqtt_host="localhost"
    ),
    
    "production": LoRaGPIOConfig(
        frequency=868000000,  # 868 MHz pour l'Europe
        tx_power=14,
        mqtt_host="mosquitto"  # Service Docker
    ),
    
    "test": LoRaGPIOConfig(
        frequency=433000000,
        tx_power=5,
        rx_timeout=0.1,
        mqtt_host="localhost"
    )
}

def get_lora_config(environment: str = "development") -> LoRaGPIOConfig:
    """Retourne la configuration pour un environnement donné"""
    return CONFIGS.get(environment, DEFAULT_LORA_CONFIG)