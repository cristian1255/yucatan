#!/bin/bash

set -e

echo "=========================================="
echo "Inicializando Airflow..."
echo "=========================================="

# Inicializar base de datos
echo "1. Inicializando base de datos..."
airflow db migrate

# Crear usuario admin
echo "2. Creando usuario admin..."
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  2>/dev/null || echo "Usuario ya existe"

# ❌ COMENTAMOS esto porque rompe en Railway
# airflow connections add 'postgres_default' ...

echo "=========================================="
echo "✅ Inicialización completada"
echo "=========================================="

echo "Iniciando webserver..."

# 🔥 ESTA ES LA CLAVE
exec airflow webserver --host 0.0.0.0 --port 8080
