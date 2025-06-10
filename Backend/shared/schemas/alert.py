"""
Schémas Pydantic pour les alertes
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class AlerteBase(BaseModel):
    """Schéma de base pour les alertes"""
    nom: str = Field(..., min_length=1, max_length=100)
    condition: str = Field(..., pattern=r'^(lt|lte|eq|gte|gt)$')
    seuil: float
    
    @validator('condition')
    def validate_condition(cls, v):
        allowed_conditions = ['lt', 'lte', 'eq', 'gte', 'gt']
        if v not in allowed_conditions:
            raise ValueError(f'Condition doit être une de: {", ".join(allowed_conditions)}')
        return v


class AlerteCreate(AlerteBase):
    """Schéma pour créer une alerte"""
    capteur_id: int
    est_active: bool = Field(default=True)


class AlerteUpdate(BaseModel):
    """Schéma pour mettre à jour une alerte"""
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    condition: Optional[str] = Field(None, pattern=r'^(lt|lte|eq|gte|gt)$')
    seuil: Optional[float] = None
    est_active: Optional[bool] = None


class AlerteResponse(AlerteBase):
    """Schéma de réponse pour les alertes"""
    id: int
    capteur_id: int
    est_active: bool
    date_creation: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AlerteWithDetails(AlerteResponse):
    """Alerte avec détails du capteur"""
    capteur_nom: str
    capteur_type: str
    capteur_unite: str
    noeud_nom: str
    espace_nom: str


class HistoriqueAlerteResponse(BaseModel):
    """Schéma de réponse pour l'historique des alertes"""
    id: int
    alerte_id: int
    declenchee_a: datetime
    resolue_a: Optional[datetime] = None
    message: Optional[str] = None
    statut: str
    
    class Config:
        from_attributes = True


class HistoriqueAlerteWithDetails(HistoriqueAlerteResponse):
    """Historique d'alerte avec détails"""
    alerte_nom: str
    capteur_nom: str
    capteur_type: str
    noeud_nom: str
    espace_nom: str
    valeur_declenchement: Optional[float] = None


class AlerteStats(BaseModel):
    """Statistiques d'alertes"""
    total_alertes: int = 0
    alertes_actives: int = 0
    declenchements_total: int = 0
    declenchements_actifs: int = 0
    derniere_alerte: Optional[datetime] = None


class AlerteListResponse(BaseModel):
    """Schéma de réponse pour les listes d'alertes"""
    alertes: List[AlerteResponse]
    total: int
    page: int
    per_page: int


class HistoriqueListResponse(BaseModel):
    """Schéma de réponse pour l'historique des alertes"""
    historique: List[HistoriqueAlerteResponse]
    total: int
    page: int
    per_page: int


class AlerteNotification(BaseModel):
    """Schéma pour les notifications d'alerte"""
    alerte_id: int
    alerte_nom: str
    capteur_nom: str
    valeur_actuelle: float
    seuil: float
    condition: str
    declenchee_a: datetime
    message: Optional[str] = None


class AlerteCheckResult(BaseModel):
    """Résultat de vérification d'alerte"""
    alerte_id: int
    capteur_id: int
    valeur_actuelle: float
    seuil: float
    condition: str
    declenchee: bool
    message: Optional[str] = None