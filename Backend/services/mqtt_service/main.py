"""
Mqtt Service GardenConnect
"""
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
import time
from shared.config import get_settings
from shared.database import init_db, close_db, check_database_connection
from shared.schemas.common import HealthCheckResponse
from services.mqtt_service.routes.mqtt import router as mqtt_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

# Configuration OAuth2 pour pointer vers le service d'auth
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://localhost:8001/auth/token",
    scopes={}
)

app = FastAPI(
    title="GardenConnect Mqtt Service",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
)

# Routes
app.include_router(mqtt_router, prefix="/api/mqtt", tags=["MQTT"])

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        timestamp=time.time(),
        version="1.0.0",
        service_name="mqtt-service",
        database=await check_database_connection(),
    )

@app.get("/")
async def root():
    return {"service": "GardenConnect Mqtt Service", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
