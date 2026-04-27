#!/bin/bash
# =============================================================================
# init_databases.sh
# Crea la base de datos 'datos_viales' en PostgreSQL si no existe.
# Se ejecuta una sola vez durante el arranque del servicio.
# =============================================================================
set -e

echo "=========================================="
echo "🗄️  Inicializando base de datos datos_viales..."
echo "=========================================="

PGHOST="${PGHOST:-postgres.railway.internal}"
PGPORT="${PGPORT:-5432}"
PGUSER="${POSTGRES_USER:-postgres}"
PGPASSWORD="${POSTGRES_PASSWORD}"
PGDATABASE="${POSTGRES_DB:-railway}"

export PGPASSWORD

# Verificar si la BD ya existe; crearla si no.
DB_EXISTS=$(psql \
  --host="$PGHOST" \
  --port="$PGPORT" \
  --username="$PGUSER" \
  --dbname="$PGDATABASE" \
  --tuples-only \
  --no-align \
  --command="SELECT 1 FROM pg_database WHERE datname = 'datos_viales';" 2>/dev/null || echo "")

if [ -z "$DB_EXISTS" ]; then
  echo "Creando base de datos 'datos_viales'..."
  psql \
    --host="$PGHOST" \
    --port="$PGPORT" \
    --username="$PGUSER" \
    --dbname="$PGDATABASE" \
    --command="CREATE DATABASE datos_viales;"
  echo "✅ Base de datos 'datos_viales' creada exitosamente."
else
  echo "ℹ️  La base de datos 'datos_viales' ya existe. Omitiendo creación."
fi

unset PGPASSWORD
