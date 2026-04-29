from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

# IMPORTAMOS EL SCRAPER Y EL PIPELINE
from pipelines.viales_scraper import obtener_urls_sct
from pipelines.viales_estrella_pipeline import run_viales_pipeline

default_args = {
    "owner": "Cristian",
    "start_date": datetime(2026, 3, 20),
    "retries": 0
}

def crear_db_transito(**kwargs):
    """
    Crea la base de datos 'transito' si no existe.
    Se conecta a la DB 'railway' usando la conexión 'postgres_transito' porque
    CREATE DATABASE no puede ejecutarse dentro de una transacción; se requiere
    autocommit.
    """
    hook = PostgresHook(postgres_conn_id="postgres_transito")
    conn = hook.get_conn()
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = 'transito';"
    )
    if not cursor.fetchone():
        cursor.execute("CREATE DATABASE transito;")
        print("Base de datos 'transito' creada exitosamente.")
    else:
        print("La base de datos 'transito' ya existe. No se requiere acción.")
    cursor.close()
    conn.close()


def ejecutar_ciclo_viales(**kwargs):
    """
    Orquesta la extracción y manda a llamar al pipeline. 
    Nota: El pipeline interno (run_viales_pipeline) debe actualizarse 
    para manejar la lógica de inserción en cascada del copo de nieve.
    """
    lista_viales = obtener_urls_sct()
    
    for item in lista_viales:
        print(f"Iniciando carga Snowflake para {item['year']} - URL: {item['url']}")
        run_viales_pipeline(url=item['url'], year=item['year'])

with DAG(
    dag_id="sct_transito_snowflake_automatizado",
    schedule_interval=None,
    catchup=False,
    default_args=default_args
) as dag:

    # PASO PREVIO: Asegurar que la base de datos 'transito' existe
    crear_base_datos_transito = PythonOperator(
        task_id="crear_base_datos_transito",
        python_callable=crear_db_transito
    )

    # IMPLEMENTACIÓN DE MODELO COPO DE NIEVE
    crear_tablas_snowflake = PostgresOperator(
        task_id="crear_tablas_snowflake",
        postgres_conn_id="postgres_transito", # Nueva base de datos de tránsito
        sql="""
        -- 1. Sub-dimensión de Rutas (Nivel más alto)
        CREATE TABLE IF NOT EXISTS dim_ruta (
            id_ruta SERIAL PRIMARY KEY,
            clave_ruta VARCHAR(50) UNIQUE -- Ej: 'MEX-180'
        );

        -- 2. Sub-dimensión de Carreteras (Relacionada con Ruta)
        CREATE TABLE IF NOT EXISTS dim_carretera (
            id_carretera SERIAL PRIMARY KEY,
            nombre_carretera VARCHAR(255),
            id_ruta INTEGER REFERENCES dim_ruta(id_ruta),
            UNIQUE(nombre_carretera, id_ruta)
        );

        -- 3. Dimensión Ubicación (Normalizada, apunta a Carretera)
        CREATE TABLE IF NOT EXISTS dim_ubicacion (
            id_ubicacion SERIAL PRIMARY KEY,
            id_carretera INTEGER REFERENCES dim_carretera(id_carretera),
            segmento_tramo VARCHAR(255),
            kilometro DECIMAL(10,2),
            latitud DECIMAL(10,6),
            longitud DECIMAL(10,6),
            UNIQUE(id_carretera, kilometro, segmento_tramo, latitud, longitud)
        );

        -- 4. Dimensiones estándar
        CREATE TABLE IF NOT EXISTS dim_vehiculo (
            id_vehiculo SERIAL PRIMARY KEY,
            clasificacion_sct VARCHAR(10) UNIQUE
        );

        CREATE TABLE IF NOT EXISTS dim_tiempo (
            id_tiempo SERIAL PRIMARY KEY,
            anio INTEGER UNIQUE
        );

        -- 5. Tabla de Hechos
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

    proceso_etl_completo = PythonOperator(
        task_id="ejecutar_scraper_y_carga_snowflake",
        python_callable=ejecutar_ciclo_viales
    )

    crear_base_datos_transito >> crear_tablas_snowflake >> proceso_etl_completo
