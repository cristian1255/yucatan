FROM apache/airflow:2.9.1-python3.12

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git postgresql-client libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar scripts y dar permisos
COPY --chown=airflow:root scripts /opt/airflow/scripts
USER root
RUN chmod +x /opt/airflow/scripts/init.sh
USER airflow

COPY dags /opt/airflow/dags
COPY config /opt/airflow/config

ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__EXECUTOR=CeleryExecutor
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV PYTHONUNBUFFERED=1

# Aumentado start-period para evitar fallos de despliegue en Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=80s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["webserver"]
