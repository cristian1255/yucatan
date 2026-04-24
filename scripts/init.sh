#!/bin/bash

set -e

echo "=========================================="
echo "Inicializando Airflow..."
echo "=========================================="

# Inicializar base de datos
echo "1. Inicializando base de datos..."
airflow db init

# Crear usuario admin
echo "2. Creando usuario admin..."
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  2>/dev/null || echo "Usuario ya existe"

# Crear conexión PostgreSQL por defecto
echo "3. Creando conexión PostgreSQL..."
airflow connections add 'postgres_default' \
  --conn-type 'postgres' \
  --conn-login 'airflow' \
  --conn-password 'airflow' \
  --conn-host 'postgres' \
  --conn-port '5432' \
  --conn-schema 'airflow' \
  2>/dev/null || echo "Conexión ya existe"

echo "=========================================="
echo "✅ Inicialización completada"
echo "=========================================="
echo ""
echo "Accede a Airflow:"
echo "  URL: http://localhost:8080"
echo "  Usuario: admin"
echo "  Contraseña: admin"
echo ""

