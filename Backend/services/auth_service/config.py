"""
Configuration spécifique au service d'authentification
"""

from shared.config import AuthServiceSettings


# Instance de configuration pour ce service
settings = AuthServiceSettings()


def get_config():
    """Récupérer la configuration du service auth"""
    return settings