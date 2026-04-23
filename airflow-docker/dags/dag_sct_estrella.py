from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# IMPORTAMOS EL NUEVO SCRAPER
from pipelines.viales_scraper import obtener_urls_sct
from pipelines.viales_estrella_pipeline import run_viales_pipeline

default_args = {
    "owner": "Cristian",
    "start_date": datetime(2026, 3, 20),
    "retries": 0
}

def ejecutar_ciclo_viales(**kwargs):
    """
    Esta función orquesta la extracción y manda a llamar al pipeline
    por cada URL encontrada por el scraper.
    """
    # 1. Ejecutar el Web Crawler de Selenium
    lista_viales = obtener_urls_sct()
    
    # 2. Por cada PDF encontrado, ejecutar el pipeline de carga
    for item in lista_viales:
        print(f"Iniciando carga para {item['year']} - URL: {item['url']}")
        run_viales_pipeline(url=item['url'], year=item['year'])

with DAG(
    dag_id="sct_viales_estrella_automatizado",
    schedule_interval=None,
    catchup=False,
    default_args=default_args
) as dag:

    crear_tablas = PostgresOperator(
        task_id="crear_tablas",
        postgres_conn_id="postgres_viales",
        sql="""
        CREATE TABLE IF NOT EXISTS dim_ubicacion (
            id_ubicacion SERIAL PRIMARY KEY,
            ruta VARCHAR(50),
            carretera VARCHAR(255),
            segmento_tramo VARCHAR(255),
            kilometro DECIMAL(10,2),
            latitud DECIMAL(10,6),
            longitud DECIMAL(10,6),
            UNIQUE(carretera, kilometro, segmento_tramo, latitud, longitud)
        );

        CREATE TABLE IF NOT EXISTS dim_vehiculo (
            id_vehiculo SERIAL PRIMARY KEY,
            clasificacion_sct VARCHAR(10) UNIQUE
        );

        CREATE TABLE IF NOT EXISTS dim_tiempo (
            id_tiempo SERIAL PRIMARY KEY,
            anio INTEGER UNIQUE
        );

        CREATE TABLE IF NOT EXISTS fact_movilidad (
            id_hecho SERIAL PRIMARY KEY,
            id_ubicacion INTEGER REFERENCES dim_ubicacion(id_ubicacion),
            id_vehiculo INTEGER REFERENCES dim_vehiculo(id_vehiculo),
            id_tiempo INTEGER REFERENCES dim_tiempo(id_tiempo),
            cantidad_vehiculos_tdpa INTEGER,
            porcentaje_composicion DECIMAL(10,2),
            UNIQUE(id_ubicacion, id_vehiculo, id_tiempo)
        );
        """
    )

    # NUEVA TAREA: Ejecuta el Crawler + La Transformación/Carga de todos los años
    proceso_etl_completo = PythonOperator(
        task_id="ejecutar_scraper_y_carga",
        python_callable=ejecutar_ciclo_viales
    )

    crear_tablas >> proceso_etl_completo