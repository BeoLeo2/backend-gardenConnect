"""
Routes de gestion des utilisateurs
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from shared.database import get_db
from shared.schemas.user import (
    UtilisateurResponse,
    UtilisateurUpdate,
    UtilisateurWithPermissions,
    RoleResponse,
    PermissionResponse,
)
from shared.schemas.common import (
    PaginationParams,
    SuccessResponse,
    FilterParams,
)
from shared.utils.auth import get_current_user_id, get_current_admin_user
from services.auth_service.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UtilisateurWithPermissions)
async def get_current_user(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Récupérer les informations de l'utilisateur connecté"""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(current_user_id)
    permissions = await user_service.get_user_permissions(current_user_id)
    
    user_response = UtilisateurResponse.from_orm(user)
    return UtilisateurWithPermissions(
        **user_response.dict(),
        permissions=permissions
    )


@router.put("/me", response_model=UtilisateurResponse)
async def update_current_user(
    user_data: UtilisateurUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Mettre à jour les informations de l'utilisateur connecté"""
    user_service = UserService(db)
    user = await user_service.update_user(current_user_id, user_data)
    
    return UtilisateurResponse.from_orm(user)


@router.get("/", response_model=List[UtilisateurResponse])
async def get_users(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    is_admin: Optional[bool] = Query(None, description="Filtrer par statut admin"),
    current_admin = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Récupérer la liste des utilisateurs (admin uniquement)"""
    user_service = UserService(db)
    
    users, total = await user_service.get_users(
        pagination=pagination,
        search=filters.search,
        is_admin=is_admin
    )
    
    return [UtilisateurResponse.from_orm(user) for user in users]


@router.get("/{user_id}", response_model=UtilisateurWithPermissions)
async def get_user(
    user_id: int,
    current_admin = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Récupérer un utilisateur par son ID (admin uniquement)"""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(user_id)
    permissions = await user_service.get_user_permissions(user_id)
    
    user_response = UtilisateurResponse.from_orm(user)
    return UtilisateurWithPermissions(
        **user_response.dict(),
        permissions=permissions
    )


@router.put("/{user_id}", response_model=UtilisateurResponse)
async def update_user(
    user_id: int,
    user_data: UtilisateurUpdate,
    current_admin = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Mettre à jour un utilisateur (admin uniquement)"""
    user_service = UserService(db)
    user = await user_service.update_user(user_id, user_data)
    
    return UtilisateurResponse.from_orm(user)


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: int,
    current_admin = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Supprimer un utilisateur (admin uniquement)"""
    user_service = UserService(db)
    success = await user_service.delete_user(user_id)
    
    if success:
        return SuccessResponse(message="Utilisateur supprimé avec succès")


@router.post("/{user_id}/make-admin", response_model=UtilisateurResponse)
async def make_admin(
    user_id: int,
    current_admin = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Promouvoir un utilisateur au rang d'administrateur"""
    user_service = UserService(db)
    user = await user_service.make_admin(user_id, current_admin.id)
    
    return UtilisateurResponse.from_orm(user)


@router.post("/{user_id}/revoke-admin", response_model=UtilisateurResponse)
async def revoke_admin(
    user_id: int,
    current_admin = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Révoquer les droits d'administrateur"""
    user_service = UserService(db)
    user = await user_service.revoke_admin(user_id, current_admin.id)
    
    return UtilisateurResponse.from_orm(user)


@router.get("/{user_id}/permissions", response_model=List[PermissionResponse])
async def get_user_permissions(
    user_id: int,
    current_admin = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Récupérer les permissions d'un utilisateur (admin uniquement)"""
    user_service = UserService(db)
    permissions = await user_service.get_user_permissions(user_id)
    
    return permissions


# Routes pour la gestion des rôles
@router.get("/roles/", response_model=List[RoleResponse])
async def get_roles(
    current_admin = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Récupérer tous les rôles disponibles (admin uniquement)"""
    user_service = UserService(db)
    roles = await user_service.get_roles()
    
    return [RoleResponse.from_orm(role) for role in roles]


@router.post("/roles/", response_model=RoleResponse)
async def create_role(
    nom: str,
    description: Optional[str] = None,
    current_admin = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Créer un nouveau rôle (admin uniquement)"""
    user_service = UserService(db)
    role = await user_service.create_role(nom, description)
    
    return RoleResponse.from_orm(role)