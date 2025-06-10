"""
Schémas Pydantic communs
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """Schéma de réponse de succès générique"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Schéma de réponse d'erreur"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


class PaginationParams(BaseModel):
    """Paramètres de pagination"""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=1000)


class PaginationInfo(BaseModel):
    """Informations de pagination"""
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class HealthCheckResponse(BaseModel):
    """Schéma de réponse pour les health checks"""
    status: str = "healthy"
    timestamp: datetime
    version: str
    service_name: str
    database: bool = False
    redis: bool = False
    mqtt: Optional[bool] = None
    details: Optional[Dict[str, Any]] = None


class MetricsResponse(BaseModel):
    """Schéma de réponse pour les métriques"""
    service_name: str
    uptime_seconds: float
    request_count: int
    error_count: int
    database_connections: int
    memory_usage_mb: float
    cpu_usage_percent: Optional[float] = None


class BulkDeleteRequest(BaseModel):
    """Schéma pour la suppression en masse"""
    ids: List[int] = Field(..., min_items=1)
    confirm: bool = Field(default=False)


class BulkDeleteResponse(BaseModel):
    """Schéma de réponse pour la suppression en masse"""
    deleted_count: int
    failed_ids: List[int] = []
    errors: List[str] = []


class FileUploadResponse(BaseModel):
    """Schéma de réponse pour l'upload de fichiers"""
    filename: str
    size: int
    content_type: str
    upload_time: datetime
    url: Optional[str] = None


class ExportResponse(BaseModel):
    """Schéma de réponse pour l'export"""
    filename: str
    format: str
    size: int
    download_url: str
    expires_at: datetime
    record_count: int


class FilterParams(BaseModel):
    """Paramètres de filtrage génériques"""
    search: Optional[str] = Field(None, max_length=100)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class SortParams(BaseModel):
    """Paramètres de tri"""
    sort_by: str = Field(default="id")
    sort_order: str = Field(default="asc", pattern=r'^(asc|desc)$')


class ConfigResponse(BaseModel):
    """Schéma de réponse pour la configuration"""
    service_name: str
    environment: str
    version: str
    features_enabled: List[str]
    limits: Dict[str, Any]