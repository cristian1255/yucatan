#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Iniciando Preparación de Airflow..."
echo "=========================================="

# 1. Migrar base de datos de Airflow
echo "Ejecutando db migrate..."
airflow db migrate

# 2. Crear usuario admin
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
if [[ "$RAILWAY_SERVICE_NAME" == *"scheduler"* ]]; then
  echo "Iniciando AIRFLOW SCHEDULER..."
  exec airflow scheduler
elif [[ "$RAILWAY_SERVICE_NAME" == *"worker"* ]]; then
  echo "Iniciando CELERY WORKER..."
  exec celery -A airflow.executors.celery_executor worker --loglevel=info
else
  echo "Iniciando AIRFLOW WEBSERVER en puerto $PORT..."
  exec airflow webserver --port $PORT
fi
