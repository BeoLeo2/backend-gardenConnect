"""
API Gateway GardenConnect
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import httpx
from contextlib import asynccontextmanager
import time

from shared.config import get_settings
from shared.schemas.common import HealthCheckResponse

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

# Configuration OAuth2 pour pointer vers le service d'auth
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://localhost:8001/auth/token",
    scopes={}
)

app = FastAPI(
    title="GardenConnect API Gateway",
    description="Point d'entrée unique pour tous les services GardenConnect",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes proxy
@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_auth(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        url = f"{settings.auth_service_url}/api/auth/{path}"
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body(),
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        if response.content:
            return response.json()
        return {}

@app.api_route("/api/data/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_data(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        url = f"{settings.data_service_url}/api/data/{path}"
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body(),
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        if response.content:
            return response.json()
        return {}

@app.api_route("/api/alerts/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_alert(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        url = f"{settings.alert_service_url}/api/alerts/{path}"
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body(),
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        if response.content:
            return response.json()
        return {}

@app.api_route("/api/mqtt/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_mqtt(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        url = f"{settings.mqtt_service_url}/api/mqtt/{path}"
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body(),
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        if response.content:
            return response.json()
        return {}

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
