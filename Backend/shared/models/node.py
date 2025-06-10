"""
Modèles nœuds Arduino
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from shared.models.base import BaseModel


class NoeudArduino(BaseModel, table=True):
    """Modèle des nœuds Arduino"""
    
    __tablename__ = "noeuds_arduino"
    
    nom: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None)
    type: str = Field(max_length=50, default="arduino_nano", index=True)
    cle_api: str = Field(max_length=100, unique=True, index=True)
    statut: str = Field(max_length=20, default="hors_ligne", index=True)
    version_firmware: Optional[str] = Field(default=None, max_length=50)
    localisation: Optional[str] = Field(default=None, max_length=100)
    derniere_connexion: Optional[datetime] = Field(default=None, index=True)
    niveau_batterie: Optional[float] = Field(default=None, index=True)
    espace_id: int = Field(foreign_key="espaces.id", index=True)
    
    # Relations
    espace: "Espace" = Relationship(back_populates="noeuds")
    capteurs: List["Capteur"] = Relationship(back_populates="noeud")


# Import pour éviter les références circulaires
from shared.models.space import Espace
from shared.models.sensor import Capteur