from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    "owner": "Cristian",
    "start_date": datetime(2026, 1, 1),
    "retries": 0,
}


def listar_tablas(**kwargs):
    """
    Lista todas las tablas existentes en el schema 'public' de Postgres-v2O8
    y las almacena en XCom para que la siguiente tarea las use.
    """
    hook = PostgresHook(postgres_conn_id="postgres_transito")
    conn = hook.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)

    tablas = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    if tablas:
        print(f"Se encontraron {len(tablas)} tabla(s) en el schema 'public':")
        for tabla in tablas:
            print(f"  - {tabla}")
    else:
        print("No se encontraron tablas en el schema 'public'. La base de datos ya está vacía.")

    # Guardamos la lista en XCom para la siguiente tarea
    kwargs["ti"].xcom_push(key="tablas_encontradas", value=tablas)
    return tablas


def eliminar_todas_las_tablas(**kwargs):
    """
    Elimina TODAS las tablas del schema 'public' usando DROP TABLE IF EXISTS ... CASCADE.
    Recupera la lista de tablas desde XCom.
    """
    ti = kwargs["ti"]
    tablas = ti.xcom_pull(task_ids="listar_tablas", key="tablas_encontradas")

    if not tablas:
        print("No hay tablas que eliminar. Se omite este paso.")
        return

    hook = PostgresHook(postgres_conn_id="postgres_transito")
    conn = hook.get_conn()
    conn.autocommit = True
    cursor = conn.cursor()

    tablas_eliminadas = []
    tablas_con_error = []

    for tabla in tablas:
        try:
            sql = f'DROP TABLE IF EXISTS public."{tabla}" CASCADE;'
            print(f"Ejecutando: {sql}")
            cursor.execute(sql)
            tablas_eliminadas.append(tabla)
            print(f"  ✓ Tabla '{tabla}' eliminada correctamente.")
        except Exception as e:
            tablas_con_error.append(tabla)
            print(f"  ✗ Error al eliminar la tabla '{tabla}': {e}")

    cursor.close()
    conn.close()

    # Guardamos el resultado en XCom para la tarea de verificación
    kwargs["ti"].xcom_push(key="tablas_eliminadas", value=tablas_eliminadas)
    kwargs["ti"].xcom_push(key="tablas_con_error", value=tablas_con_error)

    print(f"\nResumen de eliminación:")
    print(f"  Tablas eliminadas exitosamente : {len(tablas_eliminadas)}")
    print(f"  Tablas con error               : {len(tablas_con_error)}")

    if tablas_con_error:
        raise Exception(
            f"No se pudieron eliminar las siguientes tablas: {tablas_con_error}"
        )


def verificar_base_datos_vacia(**kwargs):
    """
    Verifica que el schema 'public' haya quedado completamente vacío
    y genera un resumen final de la operación.
    """
    ti = kwargs["ti"]
    tablas_originales = ti.xcom_pull(task_ids="listar_tablas", key="tablas_encontradas") or []
    tablas_eliminadas = ti.xcom_pull(task_ids="eliminar_todas_las_tablas", key="tablas_eliminadas") or []
    tablas_con_error = ti.xcom_pull(task_ids="eliminar_todas_las_tablas", key="tablas_con_error") or []

    hook = PostgresHook(postgres_conn_id="postgres_transito")
    conn = hook.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)

    tablas_restantes = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    print("=" * 60)
    print("       RESUMEN DE LIMPIEZA — Postgres-v2O8 (transito)")
    print("=" * 60)
    print(f"  Tablas encontradas originalmente : {len(tablas_originales)}")
    print(f"  Tablas eliminadas exitosamente   : {len(tablas_eliminadas)}")
    print(f"  Tablas con error                 : {len(tablas_con_error)}")
    print(f"  Tablas restantes tras limpieza   : {len(tablas_restantes)}")
    print("=" * 60)

    if tablas_eliminadas:
        print("\nTablas eliminadas:")
        for tabla in tablas_eliminadas:
            print(f"  ✓ {tabla}")

    if tablas_con_error:
        print("\nTablas con error (no eliminadas):")
        for tabla in tablas_con_error:
            print(f"  ✗ {tabla}")

    if tablas_restantes:
        print("\nTablas que aún permanecen en la base de datos:")
        for tabla in tablas_restantes:
            print(f"  ⚠ {tabla}")
        raise Exception(
            f"La base de datos NO quedó completamente vacía. "
            f"Tablas restantes: {tablas_restantes}"
        )
    else:
        print("\n✓ La base de datos Postgres-v2O8 (transito) quedó completamente vacía.")


with DAG(
    dag_id="cleanup_postgres_v2o8",
    description="Elimina TODAS las tablas del schema public en Postgres-v2O8 (transito). Solo ejecución manual.",
    schedule_interval=None,   # Solo ejecución manual
    catchup=False,
    default_args=default_args,
    tags=["cleanup", "postgres", "transito", "manual"],
) as dag:

    tarea_listar = PythonOperator(
        task_id="listar_tablas",
        python_callable=listar_tablas,
    )

    tarea_eliminar = PythonOperator(
        task_id="eliminar_todas_las_tablas",
        python_callable=eliminar_todas_las_tablas,
    )

    tarea_verificar = PythonOperator(
        task_id="verificar_base_datos_vacia",
        python_callable=verificar_base_datos_vacia,
    )

    tarea_listar >> tarea_eliminar >> tarea_verificar
