"""
Service de logique métier pour l'authentification
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlmodel import Session, select
from fastapi import HTTPException, status
import secrets

from shared.models.user import Utilisateur, TokenRafraichissement
from shared.schemas.user import UtilisateurCreate, LoginRequest
from shared.utils.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_password,
    verify_password,
    validate_password_strength,
)
from shared.utils.exceptions import (
    AuthenticationException,
    ResourceExistsException,
    ValidationException,
)
from shared.config import get_auth_settings

settings = get_auth_settings()


class AuthService:
    """Service d'authentification"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def register_user(self, user_data: UtilisateurCreate) -> Utilisateur:
        """Enregistrer un nouvel utilisateur"""
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = self.db.execute(
            select(Utilisateur).where(
                (Utilisateur.email == user_data.email) |
                (Utilisateur.nom_utilisateur == user_data.nom_utilisateur)
            )
        ).scalar_one_or_none()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise ResourceExistsException("Utilisateur", "email", user_data.email)
            else:
                raise ResourceExistsException("Utilisateur", "nom_utilisateur", user_data.nom_utilisateur)
        
        # Valider la force du mot de passe
        if not validate_password_strength(user_data.mot_de_passe):
            raise ValidationException(
                "Le mot de passe ne respecte pas les critères de sécurité",
                "mot_de_passe"
            )
        
        # Créer l'utilisateur
        hashed_password = hash_password(user_data.mot_de_passe)
        user = Utilisateur(
            nom_utilisateur=user_data.nom_utilisateur,
            email=user_data.email,
            mot_de_passe=hashed_password,
            is_admin=False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def authenticate_user(self, login_data: LoginRequest) -> Tuple[str, str, Utilisateur]:
        """Authentifier un utilisateur et retourner les tokens"""
        
        # Rechercher l'utilisateur
        user = self.db.execute(
            select(Utilisateur).where(Utilisateur.email == login_data.email)
        ).scalar_one_or_none()
        
        if not user or not verify_password(login_data.mot_de_passe, user.mot_de_passe):
            raise AuthenticationException("Email ou mot de passe incorrect")
        
        # Créer les tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token_str = create_refresh_token({"sub": str(user.id)})
        
        # Stocker le refresh token
        refresh_token = TokenRafraichissement(
            utilisateur_id=user.id,
            token=refresh_token_str,
            expire_a=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
            est_actif=True
        )
        
        self.db.add(refresh_token)
        self.db.commit()
        
        return access_token, refresh_token_str, user
    
    async def refresh_access_token(self, refresh_token_str: str) -> str:
        """Rafraîchir un token d'accès"""
        
        # Vérifier le refresh token
        try:
            payload = verify_token(refresh_token_str, "refresh")
        except AuthenticationException:
            raise AuthenticationException("Token de rafraîchissement invalide")
        
        user_id = int(payload.get("sub"))
        
        # Vérifier que le token existe et est actif
        refresh_token = self.db.execute(
            select(TokenRafraichissement).where(
                TokenRafraichissement.token == refresh_token_str,
                TokenRafraichissement.utilisateur_id == user_id,
                TokenRafraichissement.est_actif == True,
                TokenRafraichissement.expire_a > datetime.utcnow()
            )
        ).scalar_one_or_none()
        
        if not refresh_token:
            raise AuthenticationException("Token de rafraîchissement invalide ou expiré")
        
        # Créer un nouveau token d'accès
        access_token = create_access_token({"sub": str(user_id)})
        
        return access_token
    
    async def logout_user(self, refresh_token_str: str) -> bool:
        """Déconnecter un utilisateur en désactivant son refresh token"""
        
        refresh_token = self.db.execute(
            select(TokenRafraichissement).where(
                TokenRafraichissement.token == refresh_token_str,
                TokenRafraichissement.est_actif == True
            )
        ).scalar_one_or_none()
        
        if refresh_token:
            refresh_token.est_actif = False
            self.db.commit()
            return True
        
        return False
    
    async def change_password(
        self, 
        user_id: int, 
        old_password: str, 
        new_password: str
    ) -> bool:
        """Changer le mot de passe d'un utilisateur"""
        
        user = self.db.get(Utilisateur, user_id)
        if not user:
            raise AuthenticationException("Utilisateur non trouvé")
        
        # Vérifier l'ancien mot de passe
        if not verify_password(old_password, user.mot_de_passe):
            raise AuthenticationException("Ancien mot de passe incorrect")
        
        # Valider le nouveau mot de passe
        if not validate_password_strength(new_password):
            raise ValidationException(
                "Le nouveau mot de passe ne respecte pas les critères de sécurité",
                "nouveau_mot_de_passe"
            )
        
        # Mettre à jour le mot de passe
        user.mot_de_passe = hash_password(new_password)
        user.date_modification = datetime.utcnow()
        
        # Désactiver tous les refresh tokens existants
        existing_tokens = self.db.execute(
            select(TokenRafraichissement).where(
                TokenRafraichissement.utilisateur_id == user_id,
                TokenRafraichissement.est_actif == True
            )
        ).scalars().all()
        
        for token in existing_tokens:
            token.est_actif = False
        
        self.db.commit()
        return True
    
    async def request_password_reset(self, email: str) -> str:
        """Demander un reset de mot de passe"""
        
        user = self.db.execute(
            select(Utilisateur).where(Utilisateur.email == email)
        ).scalar_one_or_none()
        
        if not user:
            # Ne pas révéler si l'email existe ou non
            return "Si cet email existe, un lien de réinitialisation a été envoyé"
        
        # Générer un token de reset (simplifié ici)
        reset_token = secrets.token_urlsafe(32)
        
        # Dans un vrai système, on stockerait ce token avec une expiration
        # et on enverrait un email
        
        return "Un lien de réinitialisation a été envoyé à votre email"
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Réinitialiser un mot de passe avec un token"""
        
        # Dans un vrai système, on vérifierait le token stocké
        # Ici c'est simplifié
        
        if not validate_password_strength(new_password):
            raise ValidationException(
                "Le mot de passe ne respecte pas les critères de sécurité",
                "mot_de_passe"
            )
        
        # Cette implémentation est simplifiée
        # En production, il faudrait :
        # 1. Vérifier le token dans la base
        # 2. Vérifier qu'il n'est pas expiré
        # 3. Récupérer l'utilisateur associé
        # 4. Mettre à jour son mot de passe
        
        return True
    
    async def cleanup_expired_tokens(self) -> int:
        """Nettoyer les tokens expirés"""
        
        expired_tokens = self.db.execute(
            select(TokenRafraichissement).where(
                TokenRafraichissement.expire_a < datetime.utcnow()
            )
        ).scalars().all()
        
        count = len(expired_tokens)
        
        for token in expired_tokens:
            self.db.delete(token)
        
        self.db.commit()
        return count