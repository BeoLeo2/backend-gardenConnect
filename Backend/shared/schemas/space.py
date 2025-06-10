"""
Schémas Pydantic pour les espaces
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class EspaceBase(BaseModel):
    """Schéma de base pour les espaces"""
    nom: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    type: str = Field(..., max_length=50)
    emplacement: Optional[str] = Field(None, max_length=100)


class EspaceCreate(EspaceBase):
    """Schéma pour créer un espace"""
    espace_parent_id: Optional[int] = None


class EspaceUpdate(BaseModel):
    """Schéma pour mettre à jour un espace"""
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    type: Optional[str] = Field(None, max_length=50)
    emplacement: Optional[str] = Field(None, max_length=100)
    espace_parent_id: Optional[int] = None


class EspaceResponse(EspaceBase):
    """Schéma de réponse pour les espaces"""
    id: int
    espace_parent_id: Optional[int] = None
    date_creation: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EspaceWithHierarchy(EspaceResponse):
    """Espace avec hiérarchie"""
    parent: Optional["EspaceResponse"] = None
    enfants: List["EspaceResponse"] = []
    niveau: int = 0


class EspaceWithStats(EspaceResponse):
    """Espace avec statistiques"""
    nombre_noeuds: int = 0
    nombre_capteurs: int = 0
    nombre_alertes_actives: int = 0


class EspaceUtilisateurCreate(BaseModel):
    """Schéma pour associer un utilisateur à un espace"""
    utilisateur_id: int
    role_id: int


class EspaceUtilisateurResponse(BaseModel):
    """Schéma de réponse pour les associations espace-utilisateur"""
    utilisateur_id: int
    espace_id: int
    role_id: int
    nom_utilisateur: str
    email: str
    role_nom: str
    date_creation: datetime
    
    class Config:
        from_attributes = True


class EspaceListResponse(BaseModel):
    """Schéma de réponse pour les listes d'espaces"""
    espaces: List[EspaceResponse]
    total: int
    page: int
    per_page: int