#!/bin/bash
set -e

echo "=========================================="
echo "Inicializando Airflow en Railway..."
echo "=========================================="

# 1. Migrar base de datos
airflow db migrate

# 2. Crear usuario admin (Email es obligatorio)
airflow users create \
  --username "admin" \
  --password "admin" \
  --firstname "Admin" \
  --lastname "User" \
  --role "Admin" \
  --email "admin@example.org" || echo "Usuario ya existe"

# 3. Crear conexión PostgreSQL
# Nota: Usa las variables de entorno de Railway para los valores reales
airflow connections add 'postgres_default' \
  --conn-type 'postgres' \
  --conn-login "${POSTGRES_USER}" \
  --conn-password "${POSTGRES_PASSWORD}" \
  --conn-host 'postgres.railway.internal' \
  --conn-port '5432' \
  --conn-schema 'railway' \
  2>/dev/null || echo "Conexión ya existe"

echo "✅ Inicialización completada"
