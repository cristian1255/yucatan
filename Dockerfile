FROM apache/airflow:2.9.1-python3.12

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git postgresql-client libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dags /opt/airflow/dags
COPY config /opt/airflow/config
COPY scripts /opt/airflow/scripts

RUN chmod +x /opt/airflow/scripts/init.sh

ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__EXECUTOR=SequentialExecutor
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__WEBSERVER__WEB_SERVER_HOST=0.0.0.0
ENV AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8080
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["bash", "/opt/airflow/scripts/init.sh"]
