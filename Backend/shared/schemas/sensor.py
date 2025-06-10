"""
Schémas Pydantic pour les capteurs et données
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class CapteurBase(BaseModel):
    """Schéma de base pour les capteurs"""
    nom: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., max_length=50)
    modele: str = Field(..., max_length=50)
    emplacement: Optional[str] = Field(None, max_length=100)
    unite_mesure: str = Field(..., max_length=20)


class CapteurCreate(CapteurBase):
    """Schéma pour créer un capteur"""
    noeud_id: int
    valeur_min: Optional[float] = None
    valeur_max: Optional[float] = None
    offset_calibration: float = Field(default=0.0)


class CapteurUpdate(BaseModel):
    """Schéma pour mettre à jour un capteur"""
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    emplacement: Optional[str] = Field(None, max_length=100)
    est_actif: Optional[bool] = None
    valeur_min: Optional[float] = None
    valeur_max: Optional[float] = None
    offset_calibration: Optional[float] = None


class CapteurResponse(CapteurBase):
    """Schéma de réponse pour les capteurs"""
    id: int
    est_actif: bool
    valeur_min: Optional[float] = None
    valeur_max: Optional[float] = None
    offset_calibration: float
    noeud_id: int
    date_creation: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CapteurWithLastData(CapteurResponse):
    """Capteur avec sa dernière donnée"""
    derniere_valeur: Optional[float] = None
    derniere_mesure: Optional[datetime] = None
    noeud_nom: str = ""


class DonneesCapteurCreate(BaseModel):
    """Schéma pour créer une donnée de capteur"""
    capteur_id: int
    valeur: float
    niveau_batterie: Optional[float] = None
    horodatage: Optional[datetime] = None


class DonneesCapteurResponse(BaseModel):
    """Schéma de réponse pour les données de capteurs"""
    id: int
    capteur_id: int
    valeur: float
    horodatage: datetime
    niveau_batterie: Optional[float] = None
    
    class Config:
        from_attributes = True


class DonneesCapteurWithDetails(DonneesCapteurResponse):
    """Données de capteur avec détails"""
    capteur_nom: str
    capteur_type: str
    unite_mesure: str
    noeud_nom: str


class DataQueryParams(BaseModel):
    """Paramètres de requête pour les données"""
    capteurs_ids: Optional[List[int]] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    limit: int = Field(default=1000, ge=1, le=10000)
    offset: int = Field(default=0, ge=0)
    aggregation: Optional[str] = Field(None, pattern=r'^(avg|min|max|sum)$')
    interval: Optional[str] = Field(None, pattern=r'^(1m|5m|15m|1h|1d)$')


class DataExportParams(BaseModel):
    """Paramètres d'export de données"""
    capteurs_ids: List[int]
    start: datetime
    end: datetime
    format: str = Field(default="csv", pattern=r'^(csv|json|xlsx)$')
    include_metadata: bool = Field(default=True)


class CapteurStats(BaseModel):
    """Statistiques d'un capteur"""
    nombre_mesures: int = 0
    valeur_moyenne: Optional[float] = None
    valeur_min: Optional[float] = None
    valeur_max: Optional[float] = None
    derniere_mesure: Optional[datetime] = None
    premiere_mesure: Optional[datetime] = None


class DataAggregated(BaseModel):
    """Données agrégées"""
    horodatage: datetime
    valeur_avg: Optional[float] = None
    valeur_min: Optional[float] = None
    valeur_max: Optional[float] = None
    valeur_sum: Optional[float] = None
    count: int = 0


class CapteurListResponse(BaseModel):
    """Schéma de réponse pour les listes de capteurs"""
    capteurs: List[CapteurResponse]
    total: int
    page: int
    per_page: int


class DataListResponse(BaseModel):
    """Schéma de réponse pour les listes de données"""
    donnees: List[DonneesCapteurResponse]
    total: int
    page: int
    per_page: int
    capteur_info: Optional[CapteurResponse] = None


class LoRaMessage(BaseModel):
    """Schéma pour les messages LoRa"""
    node_id: str
    data: Dict[str, Any]
    battery_level: Optional[float] = None
    timestamp: Optional[datetime] = None
    rssi: Optional[int] = None
    snr: Optional[float] = None