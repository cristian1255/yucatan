#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Iniciando Preparación de Airflow..."
echo "=========================================="

# 1. Ajuste para compatibilidad con GitHub Actions (Evita error de SQLite + Celery)
# Si no hay una base de datos externa configurada, forzamos SequentialExecutor
if [[ -z "$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" || "$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" == *"sqlite"* ]]; then
    echo "⚠️ Detectado entorno local/test. Usando SequentialExecutor para compatibilidad..."
    export AIRFLOW__CORE__EXECUTOR=SequentialExecutor
fi

# 2. Migrar base de datos
echo "Ejecutando db migrate..."
airflow db migrate

# 3. Crear usuario admin
echo "Verificando usuario administrador..."
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.org || echo "⚠️ El usuario ya existe o no se pudo crear."

# 4. Configurar conexión predeterminada
# Usamos variables con valores por defecto para que no falle si no están presentes
echo "Configurando conexión postgres_default..."
airflow connections add 'postgres_default' \
  --conn-type 'postgres' \
  --conn-login "${POSTGRES_USER:-postgres}" \
  --conn-host "${POSTGRES_HOST:-postgres.railway.internal}" \
  --conn-port "${POSTGRES_PORT:-5432}" \
  --conn-schema "${POSTGRES_DB:-railway}" \
  --conn-password "${POSTGRES_PASSWORD}" || echo "⚠️ La conexión ya existe o faltan variables."

echo "=========================================="
echo "✅ Todo listo. Arrancando servidor..."
echo "=========================================="

if [[ "$RAILWAY_SERVICE_NAME" == *"scheduler"* ]]; then
    echo "Iniciando AIRFLOW SCHEDULER..."
    exec airflow scheduler
else
    # Si $PORT está vacío, usa 8080 por defecto (evita error de argumento vacío)
    WEB_PORT="${PORT:-8080}"
    echo "Iniciando AIRFLOW WEBSERVER en puerto $WEB_PORT..."
    exec airflow webserver --port "$WEB_PORT"
fi
