FROM apache/airflow:2.9.1-python3.12 [cite: 1]

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git postgresql-client libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt [cite: 2]

# Copiamos los scripts y aseguramos permisos
COPY --chown=airflow:root init.sh /opt/airflow/init.sh
RUN chmod +x /opt/airflow/init.sh

COPY dags /opt/airflow/dags
COPY config /opt/airflow/config

# Variables esenciales para estabilidad
ENV AIRFLOW_HOME=/opt/airflow
ENV PYTHONUNBUFFERED=1
# Genera una clave Fernet (puedes cambiarla después por una fija en producción)
ENV AIRFLOW__CORE__FERNET_KEY=7X7lR9-5X-W2u8W8x9X_Y7z6W5v4U3t2S1R0PqOnMlKj=

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1 [cite: 3]

# El comando se definirá en el Compose o script de entrada
