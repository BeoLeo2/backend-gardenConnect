"""
Service d'authentification GardenConnect
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
import time
import logging

from shared.config import get_auth_settings
from shared.database import init_db, close_db, check_database_connection, check_redis_connection
from shared.schemas.common import HealthCheckResponse, MetricsResponse
from services.auth_service.routes.auth import router as auth_router
from services.auth_service.routes.users import router as users_router

# Configuration
settings = get_auth_settings()

# Logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# Métriques
start_time = time.time()
request_count = 0
error_count = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    # Startup
    logger.info("Démarrage du service d'authentification")
    try:
        await init_db()
        logger.info("Base de données initialisée")
    except Exception as e:
        logger.error(f"Erreur d'initialisation de la base de données: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Arrêt du service d'authentification")
    await close_db()


# Application FastAPI
app = FastAPI(
    title="GardenConnect Auth Service",
    description="Service d'authentification et d'autorisation pour GardenConnect",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware de métriques
@app.middleware("http")
async def metrics_middleware(request, call_next):
    global request_count, error_count
    
    request_count += 1
    start_time_req = time.time()
    
    try:
        response = await call_next(request)
        if response.status_code >= 400:
            error_count += 1
        return response
    except Exception:
        error_count += 1
        raise
    finally:
        process_time = time.time() - start_time_req
        logger.debug(f"Request processed in {process_time:.3f}s")


# Routes
app.include_router(auth_router, prefix="/api/auth/session", tags=["Authentification"])
app.include_router(users_router, prefix="/api/auth/users", tags=["Utilisateurs"])


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check du service"""
    db_status = await check_database_connection()
    redis_status = await check_redis_connection()
    
    status = "healthy" if db_status and redis_status else "unhealthy"
    
    return HealthCheckResponse(
        status=status,
        timestamp=time.time(),
        version="1.0.0",
        service_name="auth-service",
        database=db_status,
        redis=redis_status,
    )


@app.get("/metrics", response_model=MetricsResponse)
async def metrics():
    """Métriques du service"""
    uptime = time.time() - start_time
    
    return MetricsResponse(
        service_name="auth-service",
        uptime_seconds=uptime,
        request_count=request_count,
        error_count=error_count,
        database_connections=1,  # Simplifié
        memory_usage_mb=0.0,  # À implémenter avec psutil si nécessaire
    )


@app.get("/")
async def root():
    """Route racine"""
    return {
        "service": "GardenConnect Auth Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.auth_service_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )