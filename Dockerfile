FROM apache/airflow:2.8.1

USER airflow
WORKDIR /opt/project
COPY . /opt/project

RUN pip install --no-cache-dir pandas requests beautifulsoup4 lxml psycopg2-binary

CMD ["python", "viales_estrella_pipeline.py"]
