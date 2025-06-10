"""
Configuration de base de données commune pour tous les services
"""

from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from typing import Generator, AsyncGenerator
import redis.asyncio as redis
from shared.config import get_settings

settings = get_settings()

# Moteur de base de données synchrone
if settings.database_url.startswith("sqlite"):
    # SQLite ne supporte pas les pools
    sync_engine = create_engine(
        settings.database_url,
        echo=settings.debug,
    )
else:
    # PostgreSQL avec pool
    sync_engine = create_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=300,
    )

# Moteur de base de données asynchrone
async_db_url = settings.database_url
if async_db_url.startswith("sqlite"):
    # Pour SQLite, utiliser aiosqlite
    async_db_url = async_db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif async_db_url.startswith("postgresql"):
    # Pour PostgreSQL, utiliser asyncpg
    async_db_url = async_db_url.replace("postgresql://", "postgresql+asyncpg://")

# Configuration différente selon le type de base
if async_db_url.startswith("sqlite"):
    # SQLite ne supporte pas les pools
    async_engine = create_async_engine(
        async_db_url,
        echo=settings.debug,
    )
else:
    # PostgreSQL avec pool
    async_engine = create_async_engine(
        async_db_url,
        echo=settings.debug,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=300,
    )

# Session makers
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Redis client
redis_client = None


async def get_redis() -> redis.Redis:
    """Obtenir le client Redis"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.redis_url)
    return redis_client


def get_db() -> Generator[Session, None, None]:
    """Obtenir une session de base de données synchrone"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Obtenir une session de base de données asynchrone"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def create_tables():
    """Créer toutes les tables de la base de données"""
    SQLModel.metadata.create_all(sync_engine)


def drop_tables():
    """Supprimer toutes les tables de la base de données"""
    SQLModel.metadata.drop_all(sync_engine)


async def init_db():
    """Initialiser la base de données de manière asynchrone"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db():
    """Fermer les connexions de base de données"""
    await async_engine.dispose()
    sync_engine.dispose()
    
    if redis_client:
        await redis_client.close()


# Health check functions
async def check_database_connection() -> bool:
    """Vérifier la connexion à la base de données"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception:
        return False


async def check_redis_connection() -> bool:
    """Vérifier la connexion à Redis"""
    try:
        redis_conn = await get_redis()
        await redis_conn.ping()
        return True
    except Exception:
        return False