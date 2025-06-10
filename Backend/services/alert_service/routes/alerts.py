"""
Routes pour les alertes
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_alerts():
    """Récupérer toutes les alertes"""
    return {"alerts": []}

@router.post("/")
async def create_alert():
    """Créer une nouvelle alerte"""
    return {"message": "Alert created"}