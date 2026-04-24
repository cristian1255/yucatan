#!/bin/bash

set -e

echo "Inicializando Airflow..."

# DB (usa migrate en vez de init)
airflow db migrate

# Crear usuario
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin || true

# Iniciar scheduler en background
echo "Iniciando scheduler..."
airflow scheduler &

# Iniciar webserver
echo "Iniciando webserver..."
exec airflow webserver --port $PORT --hostname 0.0.0.0
