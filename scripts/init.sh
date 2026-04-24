#!/bin/bash

set -e

echo "Inicializando Airflow..."

# IMPORTANTE: usar migrate
airflow db migrate

# Crear usuario
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin || true

# Iniciar scheduler en background
airflow scheduler &

# Iniciar webserver
exec airflow webserver --port $PORT --hostname 0.0.0.0
