"""
Configuration commune pour tous les services GardenConnect
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import os


class Settings(BaseSettings):
    """Configuration globale de l'application"""
    
    # Application
    app_name: str = "GardenConnect"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # MQTT
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    
    # LoRa
    lora_frequency: float = 868.0
    lora_spreading_factor: int = 9
    lora_bandwidth: int = 125000
    lora_device: str = "/dev/ttyUSB0"
    
    # Services URLs and Ports
    auth_service_url: str = "http://localhost:8001"
    data_service_url: str = "http://localhost:8002"
    alert_service_url: str = "http://localhost:8003"
    mqtt_service_url: str = "http://localhost:8004"
    
    auth_service_port: int = 8001
    data_service_port: int = 8002
    alert_service_port: int = 8003
    mqtt_service_port: int = 8004
    
    # Email (pour les alertes)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # Logging
    log_level: str = "INFO"
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Permettre les champs supplémentaires


class AuthServiceSettings(Settings):
    """Configuration spécifique au service d'authentification"""
    
    # Hashage des mots de passe
    password_hash_rounds: int = 12
    
    # Tokens de refresh
    refresh_token_expire_days: int = 30
    
    # Politique des mots de passe
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True


class DataServiceSettings(Settings):
    """Configuration spécifique au service de données"""
    
    # Pagination
    default_page_size: int = 50
    max_page_size: int = 1000
    
    # Rétention des données
    sensor_data_retention_days: int = 90
    aggregated_data_retention_years: int = 5
    
    # Export
    max_export_records: int = 100000


class AlertServiceSettings(Settings):
    """Configuration spécifique au service d'alertes"""
    
    # Fréquence de vérification des alertes (en secondes)
    alert_check_interval: int = 60
    
    # Délai de répétition des notifications (en minutes)
    notification_retry_delay: int = 5
    max_notification_retries: int = 3
    
    # Templates email
    email_template_dir: str = "templates/email"


class MqttServiceSettings(Settings):
    """Configuration spécifique au service MQTT"""
    
    # QoS MQTT
    mqtt_qos_sensor_data: int = 1
    mqtt_qos_alerts: int = 2
    mqtt_qos_commands: int = 1
    
    # Keep alive
    mqtt_keep_alive: int = 60
    
    # Reconnexion automatique
    mqtt_auto_reconnect: bool = True
    mqtt_reconnect_delay_min: int = 1
    mqtt_reconnect_delay_max: int = 60


# Instance globale des paramètres
settings = Settings()


def get_settings() -> Settings:
    """Récupérer les paramètres globaux"""
    return settings


def get_auth_settings() -> AuthServiceSettings:
    """Récupérer les paramètres du service auth"""
    return AuthServiceSettings()


def get_data_settings() -> DataServiceSettings:
    """Récupérer les paramètres du service data"""
    return DataServiceSettings()


def get_alert_settings() -> AlertServiceSettings:
    """Récupérer les paramètres du service alert"""
    return AlertServiceSettings()


def get_mqtt_settings() -> MqttServiceSettings:
    """Récupérer les paramètres du service MQTT"""
    return MqttServiceSettings()