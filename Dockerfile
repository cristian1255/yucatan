FROM apache/airflow:2.9.1-python3.12

USER root
# Instalamos dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git postgresql-client libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Creamos el directorio de scripts explícitamente
RUN mkdir -p /opt/airflow/scripts

# Copiamos los archivos del proyecto
COPY requirements.txt .
COPY scripts/init.sh /opt/airflow/scripts/init.sh
COPY dags /opt/airflow/dags
COPY config /opt/airflow/config

# Aseguramos permisos de ejecución y propiedad
RUN chmod +x /opt/airflow/scripts/init.sh && \
    chown -R airflow:root /opt/airflow

USER airflow
RUN pip install --no-cache-dir -r requirements.txt

ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__EXECUTOR=CeleryExecutor
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV PYTHONUNBUFFERED=1

# Tiempo de espera extendido para que Postgres arranque en Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=100s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["webserver"]
