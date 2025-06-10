"""
Schemas Pydantic pour GardenConnect
"""

from shared.schemas.common import (
    SuccessResponse,
    ErrorResponse,
    PaginationParams,
    PaginationInfo,
    HealthCheckResponse,
    MetricsResponse,
    BulkDeleteRequest,
    BulkDeleteResponse,
    FileUploadResponse,
    ExportResponse,
    FilterParams,
    SortParams,
    ConfigResponse,
)

from shared.schemas.user import (
    UtilisateurCreate,
    UtilisateurUpdate,
    UtilisateurResponse,
    UtilisateurWithPermissions,
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePasswordRequest,
    RoleResponse,
    PermissionResponse,
)

from shared.schemas.space import (
    EspaceCreate,
    EspaceUpdate,
    EspaceResponse,
    EspaceWithHierarchy,
    EspaceWithStats,
    EspaceUtilisateurCreate,
    EspaceUtilisateurResponse,
    EspaceListResponse,
)

from shared.schemas.node import (
    NoeudArduinoCreate,
    NoeudArduinoUpdate,
    NoeudArduinoResponse,
    NoeudArduinoWithCapteurs,
    NoeudArduinoStats,
    NoeudArduinoStatus,
    NoeudArduinoListResponse,
    ApiKeyResponse,
)

from shared.schemas.sensor import (
    CapteurCreate,
    CapteurUpdate,
    CapteurResponse,
    CapteurWithLastData,
    DonneesCapteurCreate,
    DonneesCapteurResponse,
    DonneesCapteurWithDetails,
    DataQueryParams,
    DataExportParams,
    CapteurStats,
    DataAggregated,
    CapteurListResponse,
    DataListResponse,
    LoRaMessage,
)

from shared.schemas.alert import (
    AlerteCreate,
    AlerteUpdate,
    AlerteResponse,
    AlerteWithDetails,
    HistoriqueAlerteResponse,
    HistoriqueAlerteWithDetails,
    AlerteStats,
    AlerteListResponse,
    HistoriqueListResponse,
    AlerteNotification,
    AlerteCheckResult,
)

__all__ = [
    # Common
    "SuccessResponse",
    "ErrorResponse",
    "PaginationParams",
    "PaginationInfo",
    "HealthCheckResponse",
    "MetricsResponse",
    "BulkDeleteRequest",
    "BulkDeleteResponse",
    "FileUploadResponse",
    "ExportResponse",
    "FilterParams",
    "SortParams",
    "ConfigResponse",
    
    # User
    "UtilisateurCreate",
    "UtilisateurUpdate",
    "UtilisateurResponse",
    "UtilisateurWithPermissions",
    "LoginRequest",
    "LoginResponse",
    "TokenResponse",
    "RefreshTokenRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "ChangePasswordRequest",
    "RoleResponse",
    "PermissionResponse",
    
    # Space
    "EspaceCreate",
    "EspaceUpdate",
    "EspaceResponse",
    "EspaceWithHierarchy",
    "EspaceWithStats",
    "EspaceUtilisateurCreate",
    "EspaceUtilisateurResponse",
    "EspaceListResponse",
    
    # Node
    "NoeudArduinoCreate",
    "NoeudArduinoUpdate",
    "NoeudArduinoResponse",
    "NoeudArduinoWithCapteurs",
    "NoeudArduinoStats",
    "NoeudArduinoStatus",
    "NoeudArduinoListResponse",
    "ApiKeyResponse",
    
    # Sensor
    "CapteurCreate",
    "CapteurUpdate",
    "CapteurResponse",
    "CapteurWithLastData",
    "DonneesCapteurCreate",
    "DonneesCapteurResponse",
    "DonneesCapteurWithDetails",
    "DataQueryParams",
    "DataExportParams",
    "CapteurStats",
    "DataAggregated",
    "CapteurListResponse",
    "DataListResponse",
    "LoRaMessage",
    
    # Alert
    "AlerteCreate",
    "AlerteUpdate",
    "AlerteResponse",
    "AlerteWithDetails",
    "HistoriqueAlerteResponse",
    "HistoriqueAlerteWithDetails",
    "AlerteStats",
    "AlerteListResponse",
    "HistoriqueListResponse",
    "AlerteNotification",
    "AlerteCheckResult",
]