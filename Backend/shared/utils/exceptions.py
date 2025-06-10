"""
Exceptions personnalisées pour GardenConnect
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class GardenConnectException(Exception):
    """Exception de base pour GardenConnect"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(GardenConnectException):
    """Exception liée à la base de données"""
    pass


class AuthenticationException(HTTPException):
    """Exception d'authentification"""
    
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationException(HTTPException):
    """Exception d'autorisation"""
    
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class ValidationException(HTTPException):
    """Exception de validation"""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        if field:
            detail = f"Validation error for field '{field}': {detail}"
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class ResourceNotFoundException(HTTPException):
    """Exception de ressource non trouvée"""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id '{identifier}' not found",
        )


class ResourceExistsException(HTTPException):
    """Exception de ressource déjà existante"""
    
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} with {field} '{value}' already exists",
        )


class SpaceHierarchyException(HTTPException):
    """Exception liée à la hiérarchie des espaces"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Space hierarchy error: {detail}",
        )


class NodeConnectionException(GardenConnectException):
    """Exception de connexion de nœud Arduino"""
    pass


class SensorException(GardenConnectException):
    """Exception liée aux capteurs"""
    pass


class LoRaException(GardenConnectException):
    """Exception liée au module LoRa"""
    pass


class MQTTException(GardenConnectException):
    """Exception liée au MQTT"""
    pass


class AlertException(GardenConnectException):
    """Exception liée aux alertes"""
    pass


class RateLimitException(HTTPException):
    """Exception de limite de taux"""
    
    def __init__(self, detail: str = "Too many requests"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )


class ServiceUnavailableException(HTTPException):
    """Exception de service indisponible"""
    
    def __init__(self, service: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service '{service}' is currently unavailable",
        )


class ConfigurationException(GardenConnectException):
    """Exception de configuration"""
    pass


class DataExportException(GardenConnectException):
    """Exception d'export de données"""
    pass


def handle_database_error(e: Exception) -> HTTPException:
    """Convertir une erreur de base de données en HTTPException"""
    if "unique constraint" in str(e).lower():
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resource already exists",
        )
    elif "foreign key constraint" in str(e).lower():
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reference to related resource",
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )