#!/usr/bin/env python3
"""
Script de génération automatique des services manquants
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def create_file(file_path, content):
    """Créer un fichier avec son contenu"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {file_path}")

def generate_data_service():
    """Générer les fichiers du service de données"""
    
    # Routes spaces
    spaces_routes = '''"""Routes de gestion des espaces"""
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
'''
    
    # Service spaces
    space_service = '''"""Service de gestion des espaces"""
from sqlmodel import Session, select
from shared.models.space import Espace
from shared.schemas.space import EspaceCreate, EspaceUpdate
from shared.utils.exceptions import ResourceNotFoundException

class SpaceService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_spaces(self, user_id: int):
        return self.db.execute(select(Espace)).all()
    
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
'''
    
    # Créer les fichiers
    create_file(BASE_DIR / "services/data_service/routes/spaces.py", spaces_routes)
    create_file(BASE_DIR / "services/data_service/services/space_service.py", space_service)
    
    # Routes similaires pour nodes, sensors, data (versions simplifiées)
    for entity in ["nodes", "sensors", "data"]:
        routes_content = f'''"""Routes {entity}"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from shared.database import get_db
from shared.utils.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_{entity}(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return {{"message": "Service {entity} en cours de développement"}}

@router.post("/")
async def create_{entity.rstrip('s')}(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return {{"message": "Création {entity} en cours de développement"}}
'''
        create_file(BASE_DIR / f"services/data_service/routes/{entity}.py", routes_content)
        
        service_content = f'''"""Service {entity}"""
from sqlmodel import Session

class {entity.title().rstrip('s')}Service:
    def __init__(self, db: Session):
        self.db = db
'''
        create_file(BASE_DIR / f"services/data_service/services/{entity.rstrip('s')}_service.py", service_content)

def generate_remaining_services():
    """Générer les services restants"""
    
    services = ["alert_service", "mqtt_service"]
    
    for service_name in services:
        # Main.py basique
        main_content = f'''"""
{service_name.replace('_', ' ').title()} GardenConnect
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import time
from shared.config import get_settings
from shared.database import init_db, close_db, check_database_connection
from shared.schemas.common import HealthCheckResponse

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(
    title="GardenConnect {service_name.replace('_', ' ').title()}",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        timestamp=time.time(),
        version="1.0.0",
        service_name="{service_name.replace('_', '-')}",
        database=await check_database_connection(),
    )

@app.get("/")
async def root():
    return {{"service": "GardenConnect {service_name.replace('_', ' ').title()}", "version": "1.0.0"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=800{3 if 'alert' in service_name else 4}, reload=True)
'''
        create_file(BASE_DIR / f"services/{service_name}/main.py", main_content)

def generate_api_gateway():
    """Générer l'API Gateway"""
    
    gateway_main = '''"""
API Gateway GardenConnect
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from contextlib import asynccontextmanager
import time

from shared.config import get_settings
from shared.schemas.common import HealthCheckResponse

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="GardenConnect API Gateway",
    description="Point d'entrée unique pour tous les services GardenConnect",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes proxy
@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_auth(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        url = f"{settings.auth_service_url}/{path}"
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body(),
        )
        return response.json()

@app.api_route("/data/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_data(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        url = f"{settings.data_service_url}/{path}"
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body(),
        )
        return response.json()

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        timestamp=time.time(),
        version="1.0.0",
        service_name="api-gateway",
        database=True,
    )

@app.get("/")
async def root():
    return {
        "service": "GardenConnect API Gateway", 
        "version": "1.0.0",
        "services": {
            "auth": settings.auth_service_url,
            "data": settings.data_service_url,
            "alert": settings.alert_service_url,
            "mqtt": settings.mqtt_service_url,
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''
    
    create_file(BASE_DIR / "services/api_gateway/main.py", gateway_main)

def generate_basic_tests():
    """Générer des tests de base"""
    
    conftest = '''"""Configuration des tests"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from shared.database import get_db

@pytest.fixture
def client():
    from services.auth_service.main import app
    return TestClient(app)

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
'''
    
    create_file(BASE_DIR / "tests/conftest.py", conftest)
    
    # Tests basiques pour chaque service
    services = ["auth_service", "data_service", "alert_service", "mqtt_service"]
    
    for service in services:
        test_content = f'''"""Tests pour {service}"""
def test_{service}_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service_name"] == "{service.replace('_', '-')}"

def test_{service}_root(client):
    response = client.get("/")
    assert response.status_code == 200
'''
        create_file(BASE_DIR / f"tests/test_{service}/test_main.py", test_content)

def main():
    """Générer tous les services manquants"""
    print("🚀 Génération des services GardenConnect...")
    
    generate_data_service()
    print("✅ Data Service généré")
    
    generate_remaining_services()
    print("✅ Alert & MQTT Services générés")
    
    generate_api_gateway()
    print("✅ API Gateway généré")
    
    generate_basic_tests()
    print("✅ Tests de base générés")
    
    print("🎉 Génération terminée ! Les services sont prêts à être testés.")
    print(f"📁 Répertoire: {BASE_DIR}")

if __name__ == "__main__":
    main()