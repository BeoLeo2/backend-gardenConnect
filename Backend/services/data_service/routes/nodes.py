"""Routes nodes"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from shared.database import get_db
from shared.utils.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_nodes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return {"message": "Service nodes en cours de développement"}

@router.post("/")
async def create_node(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return {"message": "Création nodes en cours de développement"}
