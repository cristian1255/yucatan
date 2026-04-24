FROM apache/airflow:2.9.1-python3.12

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git postgresql-client libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Asegura que el script init.sh se copie correctamente
COPY --chown=airflow:root scripts/init.sh /opt/airflow/scripts/init.sh
RUN chmod +x /opt/airflow/scripts/init.sh

ENV AIRFLOW_HOME=/opt/airflow
# CAMBIO CLAVE: Cambiar CeleryExecutor por LocalExecutor
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV PYTHONUNBUFFERED=1

CMD ["webserver"]
