"""
Modèles alertes et historique
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from shared.models.base import BaseModel


class Alerte(BaseModel, table=True):
    """Modèle des alertes configurées"""
    
    __tablename__ = "alertes"
    
    nom: str = Field(max_length=100, index=True)
    capteur_id: int = Field(foreign_key="capteurs.id", index=True)
    condition: str = Field(max_length=20, index=True)  # lt, lte, eq, gte, gt
    seuil: float = Field(index=True)
    est_active: bool = Field(default=True, index=True)
    
    # Relations
    capteur: "Capteur" = Relationship(back_populates="alertes")
    historique: List["HistoriqueAlerte"] = Relationship(back_populates="alerte")


class HistoriqueAlerte(SQLModel, table=True):
    """Historique des déclenchements d'alertes"""
    
    __tablename__ = "historique_alertes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    alerte_id: int = Field(foreign_key="alertes.id", index=True)
    declenchee_a: datetime = Field(default_factory=datetime.utcnow, index=True)
    resolue_a: Optional[datetime] = Field(default=None, index=True)
    message: Optional[str] = Field(default=None)
    statut: str = Field(max_length=20, default="active", index=True)
    
    # Relations
    alerte: "Alerte" = Relationship(back_populates="historique")


# Import pour éviter les références circulaires
from shared.models.sensor import Capteur