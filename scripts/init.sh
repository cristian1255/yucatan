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

echo "✅ Proceso de inicialización finalizado."#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Optimizando base de datos de Airflow..."
echo "=========================================="

# 1. Migrar la DB (Reemplaza a db init)
airflow db migrate

# 2. Crear usuario admin si no existe
airflow users create \
  --username "${_AIRFLOW_WWW_USER_USERNAME:-admin}" \
  --password "${_AIRFLOW_WWW_USER_PASSWORD:-admin}" \
  --firstname Admin \
  --lastname User \
  --role Admin || echo "El usuario administrador ya existe."

# 3. La conexión de Postgres ya se define por variable de entorno en Compose,
# pero si quieres dejarla fija en la UI de Airflow:
airflow connections add 'postgres_default' \
  --conn-type 'postgres' \
  --conn-login 'airflow' \
  --conn-password 'airflow' \
  --conn-host 'postgres' \
  --conn-port '5432' \
  --conn-schema 'airflow' 2>/dev/null || echo "Conexión 'postgres_default' ya existe."

echo "✅ Inicialización completada con éxito."
