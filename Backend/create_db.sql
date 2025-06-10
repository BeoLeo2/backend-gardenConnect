-- Script de création de base de données GardenConnect
-- À exécuter avec : psql -h localhost -U postgres -f create_db.sql

-- Créer l'utilisateur gardenconnect s'il n'existe pas
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'gardenconnect') THEN
        CREATE USER gardenconnect WITH PASSWORD 'password';
    END IF;
END
$$;

-- Créer la base de données
DROP DATABASE IF EXISTS gardenconnect;
CREATE DATABASE gardenconnect OWNER gardenconnect;

-- Connecter à la nouvelle base et donner les permissions
\c gardenconnect;

GRANT ALL PRIVILEGES ON DATABASE gardenconnect TO gardenconnect;
GRANT ALL PRIVILEGES ON SCHEMA public TO gardenconnect;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gardenconnect;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gardenconnect;

-- Créer l'extension TimescaleDB si disponible
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Message de confirmation
SELECT 'Base de données GardenConnect créée avec succès!' as message;