"""Routes sensors"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from shared.database import get_db
from shared.utils.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_sensors(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return {"message": "Service sensors en cours de développement"}

@router.post("/")
async def create_sensor(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return {"message": "Création sensors en cours de développement"}
