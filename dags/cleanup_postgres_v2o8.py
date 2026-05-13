from datetime import datetime
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    "owner": "Cristian",
    "start_date": datetime(2026, 1, 1),
    "retries": 0
}

with DAG(
    dag_id="cleanup_postgres_v2o8",
    schedule_interval=None,   # Solo ejecución manual
    catchup=False,
    default_args=default_args,
    description="Elimina TODAS las tablas del schema public en Postgres-v2O8 (ejecución única manual)"
) as dag:

    # PASO 1: Listar todas las tablas existentes antes de borrar
    listar_tablas = PostgresOperator(
        task_id="listar_tablas_existentes",
        postgres_conn_id="postgres_transito",
        sql="""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
        """
    )

    # PASO 2: Eliminar TODAS las tablas del schema public en cascada
    eliminar_todas_las_tablas = PostgresOperator(
        task_id="eliminar_todas_las_tablas",
        postgres_conn_id="postgres_transito",
        sql="""
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public')
            LOOP
                EXECUTE 'DROP TABLE IF EXISTS "' || r.tablename || '" CASCADE';
            END LOOP;
        END $$;
        """
    )

    # PASO 3: Verificar que no quedan tablas en el schema public
    verificar_limpieza = PostgresOperator(
        task_id="verificar_sin_tablas",
        postgres_conn_id="postgres_transito",
        sql="""
        SELECT COUNT(*) AS tablas_restantes
        FROM pg_tables
        WHERE schemaname = 'public';
        """
    )

    listar_tablas >> eliminar_todas_las_tablas >> verificar_limpieza
