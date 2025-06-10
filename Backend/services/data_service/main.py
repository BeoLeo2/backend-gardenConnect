"""
Service de données GardenConnect
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
import time
import logging

from shared.config import get_data_settings
from shared.database import init_db, close_db, check_database_connection, check_redis_connection
from shared.schemas.common import HealthCheckResponse, MetricsResponse

# Import des routes
from services.data_service.routes.spaces import router as spaces_router
from services.data_service.routes.nodes import router as nodes_router
from services.data_service.routes.sensors import router as sensors_router
from services.data_service.routes.data import router as data_router

settings = get_data_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

start_time = time.time()
request_count = 0
error_count = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Démarrage du service de données")
    await init_db()
    yield
    logger.info("Arrêt du service de données")
    await close_db()

# Configuration OAuth2 pour pointer vers le service d'auth
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://localhost:8001/auth/token",
    scopes={}
)

app = FastAPI(
    title="GardenConnect Data Service",
    description="Service de gestion des données pour GardenConnect",
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

@app.middleware("http")
async def metrics_middleware(request, call_next):
    global request_count, error_count
    request_count += 1
    try:
        response = await call_next(request)
        if response.status_code >= 400:
            error_count += 1
        return response
    except Exception:
        error_count += 1
        raise

app.include_router(spaces_router, prefix="/api/data/spaces", tags=["Espaces"])
app.include_router(nodes_router, prefix="/api/data/nodes", tags=["Nœuds"])
app.include_router(sensors_router, prefix="/api/data/sensors", tags=["Capteurs"])
app.include_router(data_router, prefix="/api/data/records", tags=["Données"])

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    db_status = await check_database_connection()
    redis_status = await check_redis_connection()
    
    return HealthCheckResponse(
        status="healthy" if db_status and redis_status else "unhealthy",
        timestamp=time.time(),
        version="1.0.0",
        service_name="data-service",
        database=db_status,
        redis=redis_status,
    )

@app.get("/metrics", response_model=MetricsResponse)
async def metrics():
    return MetricsResponse(
        service_name="data-service",
        uptime_seconds=time.time() - start_time,
        request_count=request_count,
        error_count=error_count,
        database_connections=1,
        memory_usage_mb=0.0,
    )

@app.get("/")
async def root():
    return {"service": "GardenConnect Data Service", "version": "1.0.0", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.data_service_port, reload=settings.debug)