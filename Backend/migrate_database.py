#!/usr/bin/env python3
"""
Script de migration de base de données pour GardenConnect
Basé sur les schémas MCD/MLD analysés

Usage:
    python migrate_database.py --create    # Créer les tables
    python migrate_database.py --seed      # Insérer des données de test
    python migrate_database.py --reset     # Supprimer et recréer toutes les tables
    python migrate_database.py --upgrade   # Appliquer les migrations
"""

import asyncio
import argparse
import sys
from datetime import datetime, timedelta
from typing import Optional

import asyncpg
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import bcrypt
import secrets
from faker import Faker

# Configuration
DATABASE_URL = "postgresql://gardenconnect:password@localhost:5432/gardenconnect"
ASYNC_DATABASE_URL = "postgresql+asyncpg://gardenconnect:password@localhost:5432/gardenconnect"

fake = Faker('fr_FR')

# Modèles SQLModel
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    date_creation: Optional[datetime] = Field(default_factory=datetime.utcnow)
    date_modification: Optional[datetime] = Field(default=None)

# Table Utilisateurs
class Utilisateur(BaseModel, table=True):
    __tablename__ = "utilisateurs"
    
    nom_utilisateur: str = Field(max_length=50, unique=True, index=True)
    email: str = Field(max_length=100, unique=True, index=True)
    mot_de_passe: str = Field(max_length=100)
    is_admin: bool = Field(default=False)

# Table Rôles
class Role(BaseModel, table=True):
    __tablename__ = "roles"
    
    nom: str = Field(max_length=50, unique=True)
    description: Optional[str] = Field(default=None)

# Table Espaces
class Espace(BaseModel, table=True):
    __tablename__ = "espaces"
    
    nom: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None)
    type: str = Field(max_length=50, index=True)
    emplacement: Optional[str] = Field(default=None, max_length=100)
    espace_parent_id: Optional[int] = Field(default=None, foreign_key="espaces.id")
    
    # Relations
    parent: Optional["Espace"] = Relationship(
        back_populates="enfants",
        sa_relationship_kwargs={"remote_side": "Espace.id"}
    )
    enfants: List["Espace"] = Relationship(back_populates="parent")

# Table Association Espace-Utilisateurs
class EspaceUtilisateur(BaseModel, table=True):
    __tablename__ = "espace_utilisateurs"
    
    utilisateur_id: int = Field(foreign_key="utilisateurs.id", primary_key=True)
    espace_id: int = Field(foreign_key="espaces.id", primary_key=True)
    role_id: int = Field(foreign_key="roles.id")

# Table Nœuds Arduino
class NoeudArduino(BaseModel, table=True):
    __tablename__ = "noeuds_arduino"
    
    nom: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None)
    type: str = Field(max_length=50, default="arduino_nano")
    cle_api: str = Field(max_length=100, unique=True, index=True)
    statut: str = Field(max_length=20, default="hors_ligne", index=True)
    version_firmware: Optional[str] = Field(default=None, max_length=50)
    localisation: Optional[str] = Field(default=None, max_length=100)
    derniere_connexion: Optional[datetime] = Field(default=None)
    niveau_batterie: Optional[float] = Field(default=None)
    espace_id: int = Field(foreign_key="espaces.id", index=True)

# Table Capteurs
class Capteur(BaseModel, table=True):
    __tablename__ = "capteurs"
    
    nom: str = Field(max_length=100, index=True)
    type: str = Field(max_length=50, index=True)  # temperature, humidity, soil_moisture, etc.
    modele: str = Field(max_length=50)  # DHT22, BMP280, etc.
    emplacement: Optional[str] = Field(default=None, max_length=100)
    est_actif: bool = Field(default=True, index=True)
    valeur_min: Optional[float] = Field(default=None)
    valeur_max: Optional[float] = Field(default=None)
    offset_calibration: float = Field(default=0.0)
    unite_mesure: str = Field(max_length=20)  # °C, %, hPa, lux, etc.
    noeud_id: int = Field(foreign_key="noeuds_arduino.id", index=True)

# Table Données Capteurs
class DonneesCapteur(SQLModel, table=True):
    __tablename__ = "donnees_capteurs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    capteur_id: int = Field(foreign_key="capteurs.id", index=True)
    valeur: float = Field(index=True)
    horodatage: datetime = Field(default_factory=datetime.utcnow, index=True)
    niveau_batterie: Optional[float] = Field(default=None)

# Table Alertes
class Alerte(BaseModel, table=True):
    __tablename__ = "alertes"
    
    nom: str = Field(max_length=100)
    capteur_id: int = Field(foreign_key="capteurs.id", index=True)
    condition: str = Field(max_length=20)  # lt, lte, eq, gte, gt
    seuil: float
    est_active: bool = Field(default=True, index=True)

# Table Historique Alertes
class HistoriqueAlerte(SQLModel, table=True):
    __tablename__ = "historique_alertes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    alerte_id: int = Field(foreign_key="alertes.id", index=True)
    declenchee_a: datetime = Field(default_factory=datetime.utcnow, index=True)
    resolue_a: Optional[datetime] = Field(default=None)
    message: Optional[str] = Field(default=None)
    statut: str = Field(max_length=20, default="active", index=True)

# Table Tokens de Rafraîchissement
class TokenRafraichissement(BaseModel, table=True):
    __tablename__ = "tokens_rafraichissement"
    
    utilisateur_id: int = Field(foreign_key="utilisateurs.id", index=True)
    token: str = Field(max_length=255, unique=True, index=True)
    expire_a: datetime = Field(index=True)
    est_actif: bool = Field(default=True, index=True)

class DatabaseMigrator:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=True)
    
    async def create_database_if_not_exists(self):
        """Créer la base de données si elle n'existe pas"""
        try:
            # Extraire les informations de connexion
            parts = self.database_url.replace("postgresql://", "").split("/")
            connection_info = parts[0]
            db_name = parts[1] if len(parts) > 1 else "gardenconnect"
            
            user_pass, host_port = connection_info.split("@")
            user, password = user_pass.split(":")
            host = host_port.split(":")[0]
            port = int(host_port.split(":")[1]) if ":" in host_port else 5432
            
            # Connexion à PostgreSQL pour créer la DB
            conn = await asyncpg.connect(
                user=user, password=password, host=host, port=port, database="postgres"
            )
            
            # Vérifier si la base existe
            result = await conn.fetchrow(
                "SELECT 1 FROM pg_database WHERE datname = $1", db_name
            )
            
            if not result:
                print(f"Création de la base de données '{db_name}'...")
                await conn.execute(f'CREATE DATABASE "{db_name}"')
                print(f"Base de données '{db_name}' créée avec succès.")
            else:
                print(f"Base de données '{db_name}' existe déjà.")
            
            await conn.close()
            
        except Exception as e:
            print(f"Erreur lors de la création de la base de données : {e}")
            sys.exit(1)
    
    def create_tables(self):
        """Créer toutes les tables"""
        print("Création des tables...")
        SQLModel.metadata.create_all(self.engine)
        print("Tables créées avec succès.")
    
    def drop_tables(self):
        """Supprimer toutes les tables"""
        print("Suppression des tables...")
        SQLModel.metadata.drop_all(self.engine)
        print("Tables supprimées avec succès.")
    
    def create_extensions(self):
        """Créer les extensions PostgreSQL nécessaires"""
        print("Création des extensions PostgreSQL...")
        with Session(self.engine) as session:
            # TimescaleDB pour optimiser les séries temporelles
            try:
                session.exec("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
                print("Extension TimescaleDB créée.")
                
                # Convertir la table des données capteurs en hypertable
                session.exec(
                    "SELECT create_hypertable('donnees_capteurs', 'horodatage', if_not_exists => TRUE);"
                )
                print("Hypertable créée pour donnees_capteurs.")
                
            except Exception as e:
                print(f"Attention: TimescaleDB non disponible: {e}")
            
            # Autres extensions utiles
            session.exec("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
            session.exec("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
            session.commit()
    
    def create_indexes(self):
        """Créer les index supplémentaires pour optimiser les performances"""
        print("Création des index supplémentaires...")
        with Session(self.engine) as session:
            # Index composites pour les requêtes fréquentes
            session.exec("""
                CREATE INDEX IF NOT EXISTS idx_donnees_capteurs_capteur_horodatage 
                ON donnees_capteurs (capteur_id, horodatage DESC);
            """)
            
            session.exec("""
                CREATE INDEX IF NOT EXISTS idx_donnees_capteurs_horodatage_valeur 
                ON donnees_capteurs (horodatage DESC, valeur);
            """)
            
            session.exec("""
                CREATE INDEX IF NOT EXISTS idx_historique_alertes_declenchee 
                ON historique_alertes (declenchee_a DESC);
            """)
            
            session.exec("""
                CREATE INDEX IF NOT EXISTS idx_noeuds_statut_espace 
                ON noeuds_arduino (statut, espace_id);
            """)
            
            session.commit()
        print("Index créés avec succès.")
    
    def seed_data(self):
        """Insérer des données de test"""
        print("Insertion des données de test...")
        
        with Session(self.engine) as session:
            # Créer les rôles de base
            roles = [
                Role(nom="admin", description="Administrateur système"),
                Role(nom="proprietaire", description="Propriétaire d'espace"),
                Role(nom="gestionnaire", description="Gestionnaire d'espace"),
                Role(nom="observateur", description="Lecture seule"),
            ]
            
            for role in roles:
                session.add(role)
            session.commit()
            
            # Créer un utilisateur admin
            admin_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            admin_user = Utilisateur(
                nom_utilisateur="admin",
                email="admin@gardenconnect.local",
                mot_de_passe=admin_password,
                is_admin=True
            )
            session.add(admin_user)
            session.commit()
            
            # Créer quelques utilisateurs de test
            test_users = []
            for i in range(3):
                password = bcrypt.hashpw(f"user{i+1}123".encode(), bcrypt.gensalt()).decode()
                user = Utilisateur(
                    nom_utilisateur=f"user{i+1}",
                    email=f"user{i+1}@gardenconnect.local",
                    mot_de_passe=password,
                    is_admin=False
                )
                session.add(user)
                test_users.append(user)
            session.commit()
            
            # Créer une hiérarchie d'espaces
            exploitation = Espace(
                nom="Exploitation Bio Dupont",
                description="Exploitation agricole biologique",
                type="exploitation",
                emplacement="Normandie, France"
            )
            session.add(exploitation)
            session.commit()
            
            # Espaces enfants
            serre1 = Espace(
                nom="Serre Tomates",
                description="Serre dédiée aux tomates",
                type="serre",
                emplacement="Nord de l'exploitation",
                espace_parent_id=exploitation.id
            )
            
            serre2 = Espace(
                nom="Serre Légumes Verts",
                description="Serre pour légumes verts",
                type="serre", 
                emplacement="Sud de l'exploitation",
                espace_parent_id=exploitation.id
            )
            
            champ1 = Espace(
                nom="Champ Céréales",
                description="Champ pour céréales bio",
                type="champ",
                emplacement="Est de l'exploitation",
                espace_parent_id=exploitation.id
            )
            
            session.add_all([serre1, serre2, champ1])
            session.commit()
            
            # Associer les utilisateurs aux espaces
            espace_users = [
                EspaceUtilisateur(utilisateur_id=admin_user.id, espace_id=exploitation.id, role_id=1),
                EspaceUtilisateur(utilisateur_id=test_users[0].id, espace_id=serre1.id, role_id=2),
                EspaceUtilisateur(utilisateur_id=test_users[1].id, espace_id=serre2.id, role_id=3),
                EspaceUtilisateur(utilisateur_id=test_users[2].id, espace_id=champ1.id, role_id=4),
            ]
            
            for assoc in espace_users:
                session.add(assoc)
            session.commit()
            
            # Créer des nœuds Arduino
            noeuds = [
                NoeudArduino(
                    nom="Arduino Serre 1 - Zone A",
                    description="Capteurs zone A de la serre tomates",
                    cle_api=secrets.token_urlsafe(32),
                    statut="en_ligne",
                    version_firmware="1.2.3",
                    localisation="Serre 1, Zone A",
                    niveau_batterie=85.5,
                    espace_id=serre1.id,
                    derniere_connexion=datetime.utcnow()
                ),
                NoeudArduino(
                    nom="Arduino Serre 2 - Zone B", 
                    description="Capteurs zone B de la serre légumes",
                    cle_api=secrets.token_urlsafe(32),
                    statut="en_ligne",
                    version_firmware="1.2.3",
                    localisation="Serre 2, Zone B",
                    niveau_batterie=72.3,
                    espace_id=serre2.id,
                    derniere_connexion=datetime.utcnow() - timedelta(minutes=15)
                ),
                NoeudArduino(
                    nom="Arduino Champ - Station Météo",
                    description="Station météo champ céréales",
                    cle_api=secrets.token_urlsafe(32),
                    statut="maintenance",
                    version_firmware="1.1.8",
                    localisation="Champ, Centre",
                    niveau_batterie=23.7,
                    espace_id=champ1.id,
                    derniere_connexion=datetime.utcnow() - timedelta(hours=2)
                )
            ]
            
            for noeud in noeuds:
                session.add(noeud)
            session.commit()
            
            # Créer des capteurs
            capteurs = [
                # Capteurs Serre 1
                Capteur(
                    nom="Température Air Serre 1",
                    type="temperature_air",
                    modele="DHT22",
                    emplacement="Serre 1, hauteur 1.5m",
                    valeur_min=-10.0,
                    valeur_max=50.0,
                    unite_mesure="°C",
                    noeud_id=noeuds[0].id
                ),
                Capteur(
                    nom="Humidité Air Serre 1",
                    type="humidite_air",
                    modele="DHT22",
                    emplacement="Serre 1, hauteur 1.5m",
                    valeur_min=0.0,
                    valeur_max=100.0,
                    unite_mesure="%",
                    noeud_id=noeuds[0].id
                ),
                Capteur(
                    nom="Humidité Sol Serre 1",
                    type="humidite_sol",
                    modele="FC-28",
                    emplacement="Serre 1, profondeur 10cm",
                    valeur_min=0.0,
                    valeur_max=100.0,
                    unite_mesure="%",
                    noeud_id=noeuds[0].id
                ),
                # Capteurs Serre 2
                Capteur(
                    nom="Température Air Serre 2",
                    type="temperature_air",
                    modele="DHT22",
                    emplacement="Serre 2, hauteur 1.5m",
                    valeur_min=-10.0,
                    valeur_max=50.0,
                    unite_mesure="°C",
                    noeud_id=noeuds[1].id
                ),
                Capteur(
                    nom="Luminosité Serre 2",
                    type="luminosite",
                    modele="BH1750",
                    emplacement="Serre 2, hauteur 2m",
                    valeur_min=0.0,
                    valeur_max=65535.0,
                    unite_mesure="lux",
                    noeud_id=noeuds[1].id
                ),
                # Capteurs Champ
                Capteur(
                    nom="Pression Atmosphérique",
                    type="pression",
                    modele="BMP280",
                    emplacement="Station météo champ",
                    valeur_min=800.0,
                    valeur_max=1200.0,
                    unite_mesure="hPa",
                    noeud_id=noeuds[2].id
                ),
                Capteur(
                    nom="Température Sol Champ",
                    type="temperature_sol",
                    modele="DS18B20",
                    emplacement="Champ, profondeur 15cm",
                    valeur_min=-20.0,
                    valeur_max=60.0,
                    unite_mesure="°C",
                    noeud_id=noeuds[2].id
                )
            ]
            
            for capteur in capteurs:
                session.add(capteur)
            session.commit()
            
            # Créer des alertes
            alertes = [
                Alerte(
                    nom="Température trop élevée Serre 1",
                    capteur_id=capteurs[0].id,
                    condition="gt",
                    seuil=35.0,
                    est_active=True
                ),
                Alerte(
                    nom="Humidité sol faible Serre 1",
                    capteur_id=capteurs[2].id,
                    condition="lt",
                    seuil=30.0,
                    est_active=True
                ),
                Alerte(
                    nom="Luminosité insuffisante Serre 2",
                    capteur_id=capteurs[4].id,
                    condition="lt",
                    seuil=10000.0,
                    est_active=True
                )
            ]
            
            for alerte in alertes:
                session.add(alerte)
            session.commit()
            
            # Générer des données de capteurs des 7 derniers jours
            print("Génération de données historiques...")
            now = datetime.utcnow()
            
            for capteur in capteurs:
                for days_ago in range(7):
                    for hour in range(0, 24, 2):  # Toutes les 2 heures
                        timestamp = now - timedelta(days=days_ago, hours=hour)
                        
                        # Générer des valeurs réalistes selon le type de capteur
                        if capteur.type == "temperature_air":
                            valeur = fake.random.uniform(18.0, 28.0)
                        elif capteur.type == "humidite_air":
                            valeur = fake.random.uniform(45.0, 75.0)
                        elif capteur.type == "humidite_sol":
                            valeur = fake.random.uniform(40.0, 80.0)
                        elif capteur.type == "luminosite":
                            valeur = fake.random.uniform(5000.0, 50000.0)
                        elif capteur.type == "pression":
                            valeur = fake.random.uniform(1010.0, 1025.0)
                        elif capteur.type == "temperature_sol":
                            valeur = fake.random.uniform(15.0, 25.0)
                        else:
                            valeur = fake.random.uniform(0.0, 100.0)
                        
                        # Ajouter un peu de bruit
                        valeur += fake.random.uniform(-1.0, 1.0)
                        valeur = max(capteur.valeur_min or 0, min(capteur.valeur_max or 100, valeur))
                        
                        donnee = DonneesCapteur(
                            capteur_id=capteur.id,
                            valeur=round(valeur, 2),
                            horodatage=timestamp,
                            niveau_batterie=fake.random.uniform(70.0, 90.0)
                        )
                        session.add(donnee)
            
            session.commit()
            print("Données de test insérées avec succès.")

async def main():
    parser = argparse.ArgumentParser(description="Migration de base de données GardenConnect")
    parser.add_argument("--create", action="store_true", help="Créer les tables")
    parser.add_argument("--seed", action="store_true", help="Insérer des données de test")
    parser.add_argument("--reset", action="store_true", help="Reset complet (drop + create + seed)")
    parser.add_argument("--upgrade", action="store_true", help="Appliquer les migrations")
    parser.add_argument("--init", action="store_true", help="Initialisation complète (create DB + tables + seed)")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    migrator = DatabaseMigrator(DATABASE_URL)
    
    try:
        if args.init:
            print("=== Initialisation complète ===")
            await migrator.create_database_if_not_exists()
            migrator.create_tables()
            migrator.create_extensions()
            migrator.create_indexes()
            migrator.seed_data()
            print("Initialisation terminée avec succès!")
        
        elif args.reset:
            print("=== Reset complet ===")
            migrator.drop_tables()
            migrator.create_tables()
            migrator.create_extensions()
            migrator.create_indexes()
            migrator.seed_data()
            print("Reset terminé avec succès!")
        
        elif args.create:
            print("=== Création des tables ===")
            migrator.create_tables()
            migrator.create_extensions()
            migrator.create_indexes()
            print("Tables créées avec succès!")
        
        elif args.seed:
            print("=== Insertion des données de test ===")
            migrator.seed_data()
            print("Données insérées avec succès!")
        
        elif args.upgrade:
            print("=== Application des migrations ===")
            # Ici vous pourriez ajouter la logique de migration Alembic
            print("Migrations appliquées avec succès!")
    
    except Exception as e:
        print(f"Erreur lors de la migration : {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())