"""
Schémas Pydantic pour les utilisateurs
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field, validator
try:
    from pydantic import EmailStr
except ImportError:
    from email_validator import EmailStr

class PermissionResponse(BaseModel):
    """Schéma de réponse pour les permissions"""
    espace_id: int
    espace_nom: str
    role_id: int
    role_nom: str
    
    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    """Schéma de réponse pour les rôles"""
    id: int
    nom: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class UtilisateurBase(BaseModel):
    """Schéma de base pour les utilisateurs"""
    nom_utilisateur: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UtilisateurCreate(UtilisateurBase):
    """Schéma pour créer un utilisateur"""
    mot_de_passe: str = Field(..., min_length=8)
    
    @validator('mot_de_passe')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not any(c.isupper() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not any(c.islower() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not any(c.isdigit() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v


class UtilisateurUpdate(BaseModel):
    """Schéma pour mettre à jour un utilisateur"""
    nom_utilisateur: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UtilisateurResponse(UtilisateurBase):
    """Schéma de réponse pour les utilisateurs"""
    id: int
    is_admin: bool
    date_creation: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UtilisateurWithPermissions(UtilisateurResponse):
    """Utilisateur avec ses permissions"""
    permissions: List["PermissionResponse"] = []


class LoginRequest(BaseModel):
    """Schéma pour la connexion"""
    email: EmailStr
    mot_de_passe: str


class LoginResponse(BaseModel):
    """Schéma de réponse pour la connexion"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UtilisateurResponse


class TokenResponse(BaseModel):
    """Schéma de réponse pour les tokens"""
    access_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schéma pour rafraîchir un token"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schéma pour demander un reset de mot de passe"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schéma pour confirmer un reset de mot de passe"""
    token: str
    nouveau_mot_de_passe: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Schéma pour changer de mot de passe"""
    ancien_mot_de_passe: str
    nouveau_mot_de_passe: str = Field(..., min_length=8)


