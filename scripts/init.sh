#!/bin/bash
set -e

echo "Inicializando Airflow..."

airflow db migrate

airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin || true

echo "Iniciando scheduler..."
airflow scheduler &

echo "Iniciando webserver..."
exec airflow webserver --host 0.0.0.0 --port $PORT
