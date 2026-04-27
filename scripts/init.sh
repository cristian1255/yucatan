#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Iniciando Preparación de Airflow..."
echo "=========================================="

# 1. Migrar base de datos de Airflow
# Esto asegura que las tablas internas del sistema estén listas
echo "Ejecutando db migrate..."
airflow db migrate

# 2. Crear usuario admin
# Solo lo intenta si no existe; si ya existe, continúa sin error
echo "Verificando usuario administrador..."
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.org || echo "⚠️ El usuario ya existe o no se pudo crear."

echo "=========================================="
echo "✅ Preparación lista. Detectando servicio..."
echo "=========================================="

# 3. Selector de Servicio
# Esto permite que el mismo archivo sirva para Webserver y Scheduler
if [[ "$RAILWAY_SERVICE_NAME" == *"scheduler"* ]]; then
    echo "Iniciando AIRFLOW SCHEDULER..."
    exec airflow scheduler
else
    echo "Iniciando AIRFLOW WEBSERVER en puerto $PORT..."
    exec airflow webserver --port $PORT
fi
