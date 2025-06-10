"""Routes de gestion des espaces"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import List, Optional
from shared.database import get_db
from shared.schemas.space import *
from shared.utils.auth import get_current_user
from services.data_service.services.space_service import SpaceService

router = APIRouter()

@router.get("/", response_model=List[EspaceResponse])
async def get_spaces(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = SpaceService(db)
    return await service.get_user_spaces(current_user.id)

@router.post("/", response_model=EspaceResponse)
async def create_space(space_data: EspaceCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = SpaceService(db)
    return await service.create_space(space_data, current_user.id)

@router.get("/{space_id}", response_model=EspaceResponse)
async def get_space(space_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = SpaceService(db)
    return await service.get_space(space_id, current_user.id)

@router.put("/{space_id}", response_model=EspaceResponse)
async def update_space(space_id: int, space_data: EspaceUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = SpaceService(db)
    return await service.update_space(space_id, space_data, current_user.id)

@router.delete("/{space_id}")
async def delete_space(space_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = SpaceService(db)
    return await service.delete_space(space_id, current_user.id)
