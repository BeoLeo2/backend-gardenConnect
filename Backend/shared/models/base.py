"""
Modèle de base pour tous les modèles SQLModel
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    """Modèle de base avec les champs communs"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    date_creation: Optional[datetime] = Field(default_factory=datetime.utcnow, index=True)
    date_modification: Optional[datetime] = Field(default=None, index=True)


class TimestampMixin(SQLModel):
    """Mixin pour les timestamps automatiques"""
    
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = Field(default=None, index=True)