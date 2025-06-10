#!/bin/bash

echo "🚀 Démarrage complet GardenConnect avec Docker"

# shellcheck disable=SC2164
cd /home/mderoir/Documents/Epitech/GardenConnect/Général/Général/Dev/Backend

echo "🛑 Arrêt des conteneurs existants..."
docker compose down

echo "🏗️ Construction des images Docker..."
docker compose build

echo "🐳 Démarrage de l'architecture complète..."
docker compose up -d

echo "⏳ Attente du démarrage..."
sleep 20

echo "🔍 Vérification de l'état des conteneurs..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🎉 Architecture GardenConnect complètement dockerisée !"
echo ""
echo "🌐 Services disponibles :"
echo "   📊 API Gateway:    http://localhost:8000/docs"
echo "   🔐 Auth Service:   http://auth-service:8001 (interne)"
echo "   💾 Data Service:   http://data-service:8002 (interne)"
echo "   🚨 Alert Service:  http://alert-service:8003 (interne)"
echo "   📡 MQTT Service:   http://mqtt-service:8004 (interne)"
echo ""
echo "🐳 Infrastructure :"
echo "   🐘 PostgreSQL:    localhost:5432"
echo "   📡 Redis:         localhost:6379"
echo "   🔔 MQTT:          localhost:1883"
echo ""
echo "🧪 Test principal :"
echo "   curl http://localhost:8000/health"
echo ""
echo "📋 Logs en temps réel :"
echo "   docker compose logs -f"
echo ""
echo "🛑 Pour arrêter :"
echo "   docker compose down"