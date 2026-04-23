from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import logging

logger = logging.getLogger(__name__)

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2026, 1, 1),
    "email_on_failure": False,
}

def tarea_inicial(**context):
    """Tarea inicial del pipeline"""
    logger.info("Pipeline iniciado")
    return {"status": "iniciado", "timestamp": datetime.now().isoformat()}

def tarea_final(**context):
    """Tarea final del pipeline"""
    logger.info("Pipeline completado")
    return {"status": "completado", "timestamp": datetime.now().isoformat()}

with DAG(
    dag_id="airflow_pipeline_diario",
    default_args=default_args,
    schedule_interval="0 0 * * *",  # Diario a las 00:00
    catchup=False,
    tags=["produccion"],
    description="Pipeline ETL automatizado",
) as dag:

    # Tarea 1: Verificar conexión a base de datos
    verificar_db = PostgresOperator(
        task_id="verificar_db",
        postgres_conn_id="postgres_default",
        sql="SELECT 1",
    )

    # Tarea 2: Inicio
    inicio = PythonOperator(
        task_id="inicio",
        python_callable=tarea_inicial,
        provide_context=True,
    )

    # Tarea 3: Final
    final = PythonOperator(
        task_id="final",
        python_callable=tarea_final,
        provide_context=True,
    )

    # Dependencias
    verificar_db >> inicio >> final
