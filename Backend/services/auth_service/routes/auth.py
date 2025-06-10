"""
Routes d'authentification
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from shared.database import get_db
from shared.schemas.user import (
    UtilisateurCreate,
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePasswordRequest,
    UtilisateurResponse,
)
from shared.schemas.common import SuccessResponse
from shared.utils.auth import get_current_user_id
from services.auth_service.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UtilisateurResponse)
async def register(
    user_data: UtilisateurCreate,
    db: Session = Depends(get_db)
):
    """Enregistrer un nouvel utilisateur"""
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_data)
    
    return UtilisateurResponse.from_orm(user)


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Connecter un utilisateur"""
    auth_service = AuthService(db)
    access_token, refresh_token, user = await auth_service.authenticate_user(login_data)
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UtilisateurResponse.from_orm(user)
    )


@router.post("/token", response_model=dict)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Endpoint OAuth2 pour l'authentification automatique dans Swagger"""
    from shared.schemas.user import LoginRequest
    
    # Convertir les données du formulaire OAuth2 vers notre format
    login_data = LoginRequest(
        email=form_data.username,  # OAuth2 utilise 'username' mais on attend un email
        mot_de_passe=form_data.password
    )
    
    auth_service = AuthService(db)
    access_token, refresh_token, user = await auth_service.authenticate_user(login_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Rafraîchir un token d'accès"""
    auth_service = AuthService(db)
    access_token = await auth_service.refresh_access_token(token_data.refresh_token)
    
    return TokenResponse(access_token=access_token)


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Déconnecter un utilisateur"""
    auth_service = AuthService(db)
    success = await auth_service.logout_user(token_data.refresh_token)
    
    if success:
        return SuccessResponse(message="Déconnexion réussie")
    else:
        return SuccessResponse(message="Token déjà invalide")


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Changer le mot de passe de l'utilisateur connecté"""
    auth_service = AuthService(db)
    success = await auth_service.change_password(
        current_user_id,
        password_data.ancien_mot_de_passe,
        password_data.nouveau_mot_de_passe
    )
    
    if success:
        return SuccessResponse(message="Mot de passe modifié avec succès")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de modifier le mot de passe"
        )


@router.post("/forgot-password", response_model=SuccessResponse)
async def forgot_password(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Demander une réinitialisation de mot de passe"""
    auth_service = AuthService(db)
    message = await auth_service.request_password_reset(reset_data.email)
    
    return SuccessResponse(message=message)


@router.post("/reset-password", response_model=SuccessResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Réinitialiser le mot de passe avec un token"""
    auth_service = AuthService(db)
    success = await auth_service.reset_password(
        reset_data.token,
        reset_data.nouveau_mot_de_passe
    )
    
    if success:
        return SuccessResponse(message="Mot de passe réinitialisé avec succès")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token invalide ou expiré"
        )


@router.post("/cleanup-tokens", response_model=SuccessResponse)
async def cleanup_expired_tokens(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Nettoyer les tokens expirés (admin uniquement)"""
    # Cette route pourrait être restreinte aux admins
    auth_service = AuthService(db)
    count = await auth_service.cleanup_expired_tokens()
    
    return SuccessResponse(
        message=f"{count} tokens expirés supprimés",
        data={"deleted_count": count}
    )