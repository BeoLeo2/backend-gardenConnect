"""
Modèles espaces et associations
"""

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from shared.models.base import BaseModel


class Espace(BaseModel, table=True):
    """Modèle des espaces hiérarchiques"""
    
    __tablename__ = "espaces"
    
    nom: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None)
    type: str = Field(max_length=50, index=True)  # exploitation, serre, champ, etc.
    emplacement: Optional[str] = Field(default=None, max_length=100)
    espace_parent_id: Optional[int] = Field(default=None, foreign_key="espaces.id", index=True)
    
    # Relations
    parent: Optional["Espace"] = Relationship(
        back_populates="enfants",
        sa_relationship_kwargs={"remote_side": "Espace.id"}
    )
    enfants: List["Espace"] = Relationship(back_populates="parent")
    noeuds: List["NoeudArduino"] = Relationship(back_populates="espace")
    utilisateurs: List["EspaceUtilisateur"] = Relationship(back_populates="espace")


class EspaceUtilisateur(BaseModel, table=True):
    """Association entre utilisateurs et espaces avec rôles"""
    
    __tablename__ = "espace_utilisateurs"
    
    utilisateur_id: int = Field(foreign_key="utilisateurs.id", primary_key=True)
    espace_id: int = Field(foreign_key="espaces.id", primary_key=True)
    role_id: int = Field(foreign_key="roles.id", index=True)
    
    # Relations
    utilisateur: "Utilisateur" = Relationship(back_populates="espaces")
    espace: "Espace" = Relationship(back_populates="utilisateurs")
    role: "Role" = Relationship()


# Import pour éviter les références circulaires
from shared.models.user import Utilisateur, Role
from shared.models.node import NoeudArduino