FROM apache/airflow:2.9.1-python3.12

USER root
# 1. Instalamos dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git postgresql-client libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Creamos el directorio de scripts
RUN mkdir -p /opt/airflow/scripts

# 3. Copiamos los archivos (Respetando tu estructura de carpetas)
COPY requirements.txt .
COPY scripts/init.sh /opt/airflow/scripts/init.sh
COPY dags /opt/airflow/dags
COPY config /opt/airflow/config

# 4. Aseguramos permisos de ejecución y propiedad de la carpeta
RUN chmod +x /opt/airflow/scripts/init.sh && \
    chown -R airflow:root /opt/airflow

USER airflow
# 5. Instalamos las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Variables de entorno base
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__EXECUTOR=CeleryExecutor
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV PYTHONUNBUFFERED=1

# 7. Healthcheck mejorado para evitar reinicios innecesarios en Railway
HEALTHCHECK --interval=30s --timeout=30s --start-period=150s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 🚀 REPARACIÓN CRÍTICA: 
# Usamos ENTRYPOINT para que init.sh SIEMPRE se ejecute.
# Esto permite crear el usuario admin y migrar la DB antes de arrancar.
ENTRYPOINT ["/opt/airflow/scripts/init.sh"]
