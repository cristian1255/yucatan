#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Iniciando Preparación de Airflow..."
echo "=========================================="

# 1. Migrar base de datos (Crucial para que aparezcan las tablas en Postgres)
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

# 3. Intentar crear la conexión (pero no detener el proceso si falla)
echo "Configurando conexión postgres_default..."
airflow connections add 'postgres_default' \
  --conn-type 'postgres' \
  --conn-login "${POSTGRES_USER:-postgres}" \
  --conn-host 'postgres.railway.internal' \
  --conn-port '5432' \
  --conn-schema "${POSTGRES_DB:-railway}" \
  --conn-password "${POSTGRES_PASSWORD}" || echo "⚠️ La conexión ya existe o faltan variables."

echo "=========================================="
echo "✅ Todo listo. Arrancando servidor..."
echo "=========================================="

# 3. Selector de Servicio
# Esto permite que el mismo archivo sirva para Webserver y Scheduler
if [[ "$RAILWAY_SERVICE_NAME" == *"scheduler"* ]]; then
    echo "Iniciando AIRFLOW SCHEDULER..."
    exec airflow scheduler
else
    echo "Iniciando AIRFLOW WEBSERVER en puerto $PORT..."
    exec airflow webserver --port $PORT --workers 2
fi
