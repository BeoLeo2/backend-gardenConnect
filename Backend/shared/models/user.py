"""
Modèles utilisateurs et rôles
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from shared.models.base import BaseModel


class Role(BaseModel, table=True):
    """Modèle des rôles utilisateurs"""
    
    __tablename__ = "roles"
    
    nom: str = Field(max_length=50, unique=True, index=True)
    description: Optional[str] = Field(default=None)


class Utilisateur(BaseModel, table=True):
    """Modèle des utilisateurs"""
    
    __tablename__ = "utilisateurs"
    
    nom_utilisateur: str = Field(max_length=50, unique=True, index=True)
    email: str = Field(max_length=100, unique=True, index=True)
    mot_de_passe: str = Field(max_length=100)
    is_admin: bool = Field(default=False, index=True)
    
    # Relations
    espaces: List["EspaceUtilisateur"] = Relationship(back_populates="utilisateur")
    tokens_refresh: List["TokenRafraichissement"] = Relationship(back_populates="utilisateur")


class TokenRafraichissement(BaseModel, table=True):
    """Modèle des tokens de rafraîchissement"""
    
    __tablename__ = "tokens_rafraichissement"
    
    utilisateur_id: int = Field(foreign_key="utilisateurs.id", index=True)
    token: str = Field(max_length=255, unique=True, index=True)
    expire_a: datetime = Field(index=True)
    est_actif: bool = Field(default=True, index=True)
    
    # Relations
    utilisateur: "Utilisateur" = Relationship(back_populates="tokens_refresh")


# Import nécessaire pour éviter les références circulaires
from shared.models.space import EspaceUtilisateur