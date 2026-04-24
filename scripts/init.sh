#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Inicializando Airflow con Postgres..."
echo "=========================================="

# Migrar la base de datos (reemplaza a db init)
airflow db migrate

# Crear usuario admin (usa variables de entorno del compose o valores por defecto)
airflow users create \
  --username "${_AIRFLOW_WWW_USER_USERNAME:-admin}" \
  --password "${_AIRFLOW_WWW_USER_PASSWORD:-admin}" \
  --firstname Admin \
  --lastname User \
  --role Admin || echo "El usuario administrador ya existe."

echo "✅ Proceso de inicialización finalizado."
