#!/bin/bash
set -e

airflow db migrate

airflow users create \
  --username "${_AIRFLOW_WWW_USER_USERNAME:-airflow}" \
  --password "${_AIRFLOW_WWW_USER_PASSWORD:-airflow}" \
  --firstname Admin \
  --lastname User \
  --role Admin || echo "Usuario ya existe"

airflow connections add 'postgres_default' \
  --conn-type 'postgres' \
  --conn-login "${POSTGRES_USER:-airflow}" \
  --conn-password "${POSTGRES_PASSWORD:-airflow}" \
  --conn-host 'postgres.railway.internal' \
  --conn-port '5432' \
  --conn-schema "${POSTGRES_DB:-airflow}" \
  2>/dev/null || echo "Conexión ya existe"
