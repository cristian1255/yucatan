#!/bin/bash
set -e

echo "1. Migrando base de datos..."
airflow db migrate

echo "2. Creando usuario admin..."
airflow users create \
  --username "admin" \
  --password "admin" \
  --firstname "Admin" \
  --lastname "User" \
  --role "Admin" \
  --email "admin@example.org" || echo "El usuario ya existe"

echo "✅ Inicialización completada"
