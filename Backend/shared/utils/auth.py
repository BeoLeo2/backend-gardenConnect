"""
Utilitaires d'authentification et d'autorisation
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
import secrets

from shared.config import get_settings
from shared.database import get_db
from shared.utils.exceptions import AuthenticationException, AuthorizationException

settings = get_settings()

# Configuration du hashage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration de l'authentification Bearer
security = HTTPBearer()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Créer un token d'accès JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Créer un token de rafraîchissement"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Vérifier un token JWT"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        
        if payload.get("type") != token_type:
            raise AuthenticationException("Invalid token type")
        
        return payload
        
    except JWTError:
        raise AuthenticationException("Could not validate credentials")


def hash_password(password: str) -> str:
    """Hasher un mot de passe"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_password_reset_token() -> str:
    """Générer un token de reset de mot de passe"""
    return secrets.token_urlsafe(32)


def generate_api_key() -> str:
    """Générer une clé API pour les nœuds Arduino"""
    return secrets.token_urlsafe(32)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """Obtenir l'ID de l'utilisateur actuel à partir du token"""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise AuthenticationException()
    
    return int(user_id)


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obtenir l'utilisateur actuel"""
    from shared.models.user import Utilisateur
    
    user = db.get(Utilisateur, user_id)
    if user is None:
        raise AuthenticationException()
    
    return user


async def get_current_admin_user(
    current_user = Depends(get_current_user)
):
    """Obtenir l'utilisateur admin actuel"""
    if not current_user.is_admin:
        raise AuthorizationException("Admin access required")
    
    return current_user


def validate_password_strength(password: str) -> bool:
    """Valider la force d'un mot de passe"""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return has_upper and has_lower and has_digit and has_special


async def check_user_space_permission(
    user_id: int,
    space_id: int,
    required_permission: str,
    db: Session
) -> bool:
    """Vérifier les permissions d'un utilisateur sur un espace"""
    from shared.models.space import EspaceUtilisateur
    from shared.models.user import Role
    
    # Requête pour récupérer les permissions de l'utilisateur sur l'espace
    # (incluant les espaces parents pour l'héritage)
    query = select(EspaceUtilisateur, Role).join(Role).where(
        EspaceUtilisateur.utilisateur_id == user_id,
        EspaceUtilisateur.espace_id == space_id
    )
    
    result = db.exec(query).first()
    
    if not result:
        return False
    
    espace_utilisateur, role = result
    
    # Logique de vérification des permissions selon le rôle
    permission_map = {
        "admin": ["read", "write", "delete", "admin"],
        "proprietaire": ["read", "write", "delete"],
        "gestionnaire": ["read", "write"],
        "observateur": ["read"]
    }
    
    allowed_permissions = permission_map.get(role.nom, [])
    return required_permission in allowed_permissions


class RequirePermission:
    """Décorateur de dépendance pour vérifier les permissions sur un espace"""
    
    def __init__(self, permission: str):
        self.permission = permission
    
    async def __call__(
        self,
        space_id: int,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # Les admins ont tous les droits
        if current_user.is_admin:
            return current_user
        
        has_permission = await check_user_space_permission(
            current_user.id, space_id, self.permission, db
        )
        
        if not has_permission:
            raise AuthorizationException(
                f"Permission '{self.permission}' required for this action"
            )
        
        return current_user


# Instances des décorateurs de permissions
require_read = RequirePermission("read")
require_write = RequirePermission("write")
require_delete = RequirePermission("delete")
require_admin = RequirePermission("admin")