"""
Service de gestion des utilisateurs
"""

from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select, func
from fastapi import HTTPException

from shared.models.user import Utilisateur, Role
from shared.models.space import EspaceUtilisateur, Espace
from shared.schemas.user import UtilisateurUpdate, PermissionResponse
from shared.utils.exceptions import ResourceNotFoundException, ResourceExistsException
from shared.schemas.common import PaginationParams


class UserService:
    """Service de gestion des utilisateurs"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[Utilisateur]:
        """Récupérer un utilisateur par son ID"""
        return self.db.get(Utilisateur, user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[Utilisateur]:
        """Récupérer un utilisateur par son email"""
        return self.db.execute(
            select(Utilisateur).where(Utilisateur.email == email)
        ).scalar_one_or_none()
    
    async def get_users(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        is_admin: Optional[bool] = None
    ) -> tuple[List[Utilisateur], int]:
        """Récupérer la liste des utilisateurs avec pagination"""
        
        query = select(Utilisateur)
        
        # Filtres
        if search:
            query = query.where(
                (Utilisateur.nom_utilisateur.contains(search)) |
                (Utilisateur.email.contains(search))
            )
        
        if is_admin is not None:
            query = query.where(Utilisateur.is_admin == is_admin)
        
        # Compter le total
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar_one()
        
        # Pagination
        offset = (pagination.page - 1) * pagination.per_page
        query = query.offset(offset).limit(pagination.per_page)
        
        users = self.db.execute(query).scalars().all()
        
        return users, total
    
    async def update_user(self, user_id: int, user_data: UtilisateurUpdate) -> Utilisateur:
        """Mettre à jour un utilisateur"""
        
        user = self.db.get(Utilisateur, user_id)
        if not user:
            raise ResourceNotFoundException("Utilisateur", user_id)
        
        # Vérifier l'unicité de l'email et du nom d'utilisateur
        if user_data.email and user_data.email != user.email:
            existing = self.db.execute(
                select(Utilisateur).where(
                    Utilisateur.email == user_data.email,
                    Utilisateur.id != user_id
                )
            ).scalar_one_or_none()
            if existing:
                raise ResourceExistsException("Utilisateur", "email", user_data.email)
        
        if user_data.nom_utilisateur and user_data.nom_utilisateur != user.nom_utilisateur:
            existing = self.db.execute(
                select(Utilisateur).where(
                    Utilisateur.nom_utilisateur == user_data.nom_utilisateur,
                    Utilisateur.id != user_id
                )
            ).scalar_one_or_none()
            if existing:
                raise ResourceExistsException("Utilisateur", "nom_utilisateur", user_data.nom_utilisateur)
        
        # Mettre à jour les champs modifiés
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.date_modification = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Supprimer un utilisateur"""
        
        user = self.db.get(Utilisateur, user_id)
        if not user:
            raise ResourceNotFoundException("Utilisateur", user_id)
        
        # Vérifier que ce n'est pas le dernier admin
        if user.is_admin:
            admin_count = self.db.execute(
                select(func.count()).where(Utilisateur.is_admin == True)
            ).scalar_one()
            
            if admin_count <= 1:
                raise HTTPException(
                    status_code=400,
                    detail="Impossible de supprimer le dernier administrateur"
                )
        
        self.db.delete(user)
        self.db.commit()
        
        return True
    
    async def get_user_permissions(self, user_id: int) -> List[PermissionResponse]:
        """Récupérer les permissions d'un utilisateur"""
        
        user = self.db.get(Utilisateur, user_id)
        if not user:
            raise ResourceNotFoundException("Utilisateur", user_id)
        
        if user.is_admin:
            # Les admins ont accès à tout
            return []  # Retourner une liste vide signifie "accès total"
        
        # Récupérer les permissions explicites
        query = select(EspaceUtilisateur, Espace, Role).join(
            Espace, EspaceUtilisateur.espace_id == Espace.id
        ).join(
            Role, EspaceUtilisateur.role_id == Role.id
        ).where(
            EspaceUtilisateur.utilisateur_id == user_id
        )
        
        results = self.db.execute(query).all()
        
        permissions = []
        for espace_user, espace, role in results:
            permissions.append(PermissionResponse(
                espace_id=espace.id,
                espace_nom=espace.nom,
                role={
                    "id": role.id,
                    "nom": role.nom,
                    "description": role.description
                }
            ))
        
        return permissions
    
    async def make_admin(self, user_id: int, current_admin_id: int) -> Utilisateur:
        """Promouvoir un utilisateur au rang d'administrateur"""
        
        # Vérifier que l'utilisateur actuel est admin
        current_admin = self.db.get(Utilisateur, current_admin_id)
        if not current_admin or not current_admin.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Seuls les administrateurs peuvent promouvoir d'autres utilisateurs"
            )
        
        user = self.db.get(Utilisateur, user_id)
        if not user:
            raise ResourceNotFoundException("Utilisateur", user_id)
        
        user.is_admin = True
        user.date_modification = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def revoke_admin(self, user_id: int, current_admin_id: int) -> Utilisateur:
        """Révoquer les droits d'administrateur"""
        
        # Vérifier que l'utilisateur actuel est admin
        current_admin = self.db.get(Utilisateur, current_admin_id)
        if not current_admin or not current_admin.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Seuls les administrateurs peuvent révoquer les droits"
            )
        
        # Empêcher l'auto-révocation
        if user_id == current_admin_id:
            raise HTTPException(
                status_code=400,
                detail="Impossible de révoquer ses propres droits d'administrateur"
            )
        
        user = self.db.get(Utilisateur, user_id)
        if not user:
            raise ResourceNotFoundException("Utilisateur", user_id)
        
        # Vérifier qu'il restera au moins un admin
        admin_count = self.db.execute(
            select(func.count()).where(Utilisateur.is_admin == True)
        ).scalar_one()
        
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Impossible de révoquer le dernier administrateur"
            )
        
        user.is_admin = False
        user.date_modification = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def get_roles(self) -> List[Role]:
        """Récupérer tous les rôles disponibles"""
        return self.db.execute(select(Role)).scalars().all()
    
    async def create_role(self, nom: str, description: Optional[str] = None) -> Role:
        """Créer un nouveau rôle"""
        
        # Vérifier l'unicité
        existing = self.db.execute(
            select(Role).where(Role.nom == nom)
        ).scalar_one_or_none()
        
        if existing:
            raise ResourceExistsException("Rôle", "nom", nom)
        
        role = Role(nom=nom, description=description)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        
        return role