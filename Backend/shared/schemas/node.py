"""
Schémas Pydantic pour les nœuds Arduino
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class NoeudArduinoBase(BaseModel):
    """Schéma de base pour les nœuds Arduino"""
    nom: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    type: str = Field(default="arduino_nano", max_length=50)
    localisation: Optional[str] = Field(None, max_length=100)


class NoeudArduinoCreate(NoeudArduinoBase):
    """Schéma pour créer un nœud Arduino"""
    espace_id: int
    version_firmware: Optional[str] = Field(None, max_length=50)


class NoeudArduinoUpdate(BaseModel):
    """Schéma pour mettre à jour un nœud Arduino"""
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    localisation: Optional[str] = Field(None, max_length=100)
    version_firmware: Optional[str] = Field(None, max_length=50)
    espace_id: Optional[int] = None


class NoeudArduinoResponse(NoeudArduinoBase):
    """Schéma de réponse pour les nœuds Arduino"""
    id: int
    cle_api: str
    statut: str
    version_firmware: Optional[str] = None
    derniere_connexion: Optional[datetime] = None
    niveau_batterie: Optional[float] = None
    espace_id: int
    date_creation: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NoeudArduinoWithCapteurs(NoeudArduinoResponse):
    """Nœud Arduino avec ses capteurs"""
    capteurs: List["CapteurResponse"] = []
    espace_nom: str = ""


class NoeudArduinoStats(BaseModel):
    """Statistiques d'un nœud Arduino"""
    nombre_capteurs: int = 0
    capteurs_actifs: int = 0
    derniere_donnee: Optional[datetime] = None
    niveau_batterie: Optional[float] = None
    temps_fonctionnement: Optional[int] = None  # en heures


class NoeudArduinoStatus(BaseModel):
    """Statut d'un nœud Arduino"""
    statut: str
    derniere_connexion: Optional[datetime] = None
    niveau_batterie: Optional[float] = None
    version_firmware: Optional[str] = None
    
    @validator('statut')
    def validate_statut(cls, v):
        allowed_statuts = ['en_ligne', 'hors_ligne', 'maintenance', 'erreur']
        if v not in allowed_statuts:
            raise ValueError(f'Statut doit être un de: {", ".join(allowed_statuts)}')
        return v


class NoeudArduinoListResponse(BaseModel):
    """Schéma de réponse pour les listes de nœuds"""
    noeuds: List[NoeudArduinoResponse]
    total: int
    page: int
    per_page: int


class ApiKeyResponse(BaseModel):
    """Schéma de réponse pour les clés API"""
    cle_api: str
    noeud_id: int


# Import pour éviter les références circulaires
from shared.schemas.sensor import CapteurResponse