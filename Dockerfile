FROM apache/airflow:2.9.1-python3.12

USER root
# Instalamos dependencias del sistema [cite: 4]
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git postgresql-client libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt .
# Instalamos librerías de Python [cite: 5]
RUN pip install --no-cache-dir -r requirements.txt

# CRUCIAL: Copiar el script con los permisos correctos
COPY --chown=airflow:root scripts/init.sh /opt/airflow/scripts/init.sh
RUN chmod +x /opt/airflow/scripts/init.sh

# Copiamos el resto de tu proyecto [cite: 4]
COPY dags /opt/airflow/dags
COPY config /opt/airflow/config

# Variables de entorno base [cite: 4]
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__EXECUTOR=CeleryExecutor
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV PYTHONUNBUFFERED=1

# Healthcheck para que Railway sepa que el servicio está vivo 
HEALTHCHECK --interval=30s --timeout=10s --start-period=80s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["webserver"]
