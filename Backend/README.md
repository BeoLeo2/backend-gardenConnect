# GardenConnect Backend

Backend microservices pour le système IoT GardenConnect utilisant FastAPI, SQLModel et PostgreSQL.

## Architecture

Architecture microservices avec 5 services principaux :

- **API Gateway** (port 8000) - Point d'entrée unique
- **Auth Service** (port 8001) - Authentification et autorisation
- **Data Service** (port 8002) - Gestion des données capteurs
- **Alert Service** (port 8003) - Alertes et notifications
- **MQTT Service** (port 8004) - Communication LoRa/MQTT

## Prérequis

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker et Docker Compose (optionnel)

## Installation

### 1. Cloner et configurer l'environnement

```bash
# Copier le fichier d'environnement
cp .env.example .env

# Modifier les variables d'environnement
nano .env
```

### 2. Installation avec Docker (Recommandé)

```bash
# Lancer tous les services
docker-compose up -d

# Initialiser la base de données
docker-compose exec api-gateway python migrate_database.py --init
```

### 3. Installation manuelle

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements/dev.txt

# Initialiser la base de données
python migrate_database.py --init

# Lancer les services individuellement
uvicorn services.api_gateway.main:app --port 8000 --reload &
uvicorn services.auth_service.main:app --port 8001 --reload &
uvicorn services.data_service.main:app --port 8002 --reload &
uvicorn services.alert_service.main:app --port 8003 --reload &
uvicorn services.mqtt_service.main:app --port 8004 --reload &
```

## Structure du projet

```
backend/
├── shared/                    # Code partagé
│   ├── models/               # Modèles SQLModel
│   ├── schemas/              # Schémas Pydantic
│   ├── utils/                # Utilitaires (auth, exceptions...)
│   ├── config.py            # Configuration
│   └── database.py          # Configuration DB
├── services/                 # Microservices
│   ├── api_gateway/         # API Gateway
│   ├── auth_service/        # Service Auth
│   ├── data_service/        # Service Data
│   ├── alert_service/       # Service Alert
│   └── mqtt_service/        # Service MQTT
├── tests/                   # Tests
├── docker/                  # Configuration Docker
├── requirements/            # Dépendances Python
└── migrate_database.py      # Script de migration
```

## Commandes utiles

### Base de données

```bash
# Créer les tables
python migrate_database.py --create

# Insérer des données de test
python migrate_database.py --seed

# Reset complet
python migrate_database.py --reset

# Initialisation complète
python migrate_database.py --init
```

### Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=. --cov-report=html

# Tests d'un service spécifique
pytest tests/test_auth_service/
```

### Docker

```bash
# Construire les images
docker-compose build

# Lancer en arrière-plan
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Avec monitoring (Prometheus/Grafana)
docker-compose --profile monitoring up -d
```

## Configuration

### Variables d'environnement principales

```env
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/gardenconnect

# JWT
JWT_SECRET_KEY=your-secret-key

# MQTT
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883

# Services
AUTH_SERVICE_URL=http://localhost:8001
DATA_SERVICE_URL=http://localhost:8002
```

### Configuration des services

Chaque service peut être configuré via :
- Variables d'environnement
- Fichier `.env`
- Configuration par défaut dans `shared/config.py`

## API Documentation

Une fois les services lancés :

- **API Gateway** : http://localhost:8000/docs
- **Auth Service** : http://localhost:8001/docs
- **Data Service** : http://localhost:8002/docs
- **Alert Service** : http://localhost:8003/docs
- **MQTT Service** : http://localhost:8004/docs

## Monitoring

### Health Checks

Chaque service expose un endpoint `/health` :

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
# etc.
```

### Métriques Prometheus

Métriques disponibles sur le port 9090 de chaque service :

```bash
curl http://localhost:8000/metrics
```

### Grafana (optionnel)

Dashboard disponible sur http://localhost:3000
- Login : admin/admin

## Développement

### Linting et formatage

```bash
# Formatage du code
black .
isort .

# Vérification du style
flake8 .
mypy .
```

### Pre-commit hooks

```bash
# Installer les hooks
pre-commit install

# Lancer manuellement
pre-commit run --all-files
```

### Ajout d'un nouveau service

1. Créer la structure dans `services/nouveau_service/`
2. Ajouter le Dockerfile dans `docker/`
3. Mettre à jour `docker-compose.yml`
4. Ajouter les routes dans l'API Gateway

## Production

### Déploiement

1. Configurer les variables d'environnement de production
2. Utiliser `requirements/prod.txt`
3. Configurer HTTPS avec un reverse proxy (nginx)
4. Activer le monitoring et les logs

### Sécurité

- Changer tous les secrets par défaut
- Activer l'authentification MQTT
- Configurer un pare-feu
- Utiliser HTTPS en production
- Activer les logs d'audit

## Troubleshooting

### Problèmes courants

1. **Erreur de connexion à la base** : Vérifier PostgreSQL et les credentials
2. **Service non accessible** : Vérifier les ports et le réseau Docker
3. **Erreur MQTT** : Vérifier Mosquitto et la configuration
4. **Erreur LoRa** : Vérifier le device `/dev/ttyUSB0` et les permissions

### Logs

```bash
# Logs Docker
docker-compose logs -f service-name

# Logs application
tail -f logs/app.log
```

## Contribution

1. Suivre les conventions de code (Black, isort, flake8)
2. Écrire des tests pour les nouvelles fonctionnalités
3. Mettre à jour la documentation
4. Utiliser les types hints

## Support

Pour toute question ou problème :
- Consulter la documentation dans `DocumentsApplicatifs/`
- Vérifier les logs des services
- Tester les health checks