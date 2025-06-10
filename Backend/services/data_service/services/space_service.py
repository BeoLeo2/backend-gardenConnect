"""Service de gestion des espaces"""
from sqlmodel import Session, select
from shared.models.space import Espace
from shared.schemas.space import EspaceCreate, EspaceUpdate
from shared.utils.exceptions import ResourceNotFoundException

class SpaceService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_spaces(self, user_id: int):
        return self.db.execute(select(Espace)).scalars().all()
    
    async def create_space(self, space_data: EspaceCreate, user_id: int):
        space = Espace(**space_data.dict())
        self.db.add(space)
        self.db.commit()
        self.db.refresh(space)
        return space
    
    async def get_space(self, space_id: int, user_id: int):
        space = self.db.get(Espace, space_id)
        if not space:
            raise ResourceNotFoundException("Espace", space_id)
        return space
    
    async def update_space(self, space_id: int, space_data: EspaceUpdate, user_id: int):
        space = await self.get_space(space_id, user_id)
        for field, value in space_data.dict(exclude_unset=True).items():
            setattr(space, field, value)
        self.db.commit()
        self.db.refresh(space)
        return space
    
    async def delete_space(self, space_id: int, user_id: int):
        space = await self.get_space(space_id, user_id)
        self.db.delete(space)
        self.db.commit()
        return {"message": "Espace supprimé"}
