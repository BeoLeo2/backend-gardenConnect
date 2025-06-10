"""
Modèles capteurs et données
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from shared.models.base import BaseModel


class Capteur(BaseModel, table=True):
    """Modèle des capteurs"""
    
    __tablename__ = "capteurs"
    
    nom: str = Field(max_length=100, index=True)
    type: str = Field(max_length=50, index=True)  # temperature_air, humidity, etc.
    modele: str = Field(max_length=50, index=True)  # DHT22, BMP280, etc.
    emplacement: Optional[str] = Field(default=None, max_length=100)
    est_actif: bool = Field(default=True, index=True)
    valeur_min: Optional[float] = Field(default=None)
    valeur_max: Optional[float] = Field(default=None)
    offset_calibration: float = Field(default=0.0)
    unite_mesure: str = Field(max_length=20, index=True)  # °C, %, hPa, lux, etc.
    noeud_id: int = Field(foreign_key="noeuds_arduino.id", index=True)
    
    # Relations
    noeud: "NoeudArduino" = Relationship(back_populates="capteurs")
    donnees: List["DonneesCapteur"] = Relationship(back_populates="capteur")
    alertes: List["Alerte"] = Relationship(back_populates="capteur")


class DonneesCapteur(SQLModel, table=True):
    """Modèle des données de capteurs (série temporelle)"""
    
    __tablename__ = "donnees_capteurs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    capteur_id: int = Field(foreign_key="capteurs.id", index=True)
    valeur: float = Field(index=True)
    horodatage: datetime = Field(default_factory=datetime.utcnow, index=True)
    niveau_batterie: Optional[float] = Field(default=None)
    
    # Relations
    capteur: "Capteur" = Relationship(back_populates="donnees")


# Import pour éviter les références circulaires
from shared.models.node import NoeudArduino
from shared.models.alert import Alerte