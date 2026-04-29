import pdfplumber
import requests
import tempfile
import re
import logging
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger("airflow.task")


# =========================
# LIMPIEZA
# =========================
def clean_text(val):
    if not val:
        return ""
    return str(val).replace("\n", " ").strip()

# =========================
# EXTRAER RUTA DESDE CLAVE
# =========================
def extraer_ruta(texto):
    if not texto:
        return None

    match = re.search(r'RUTA\s*:\s*([A-Z0-9\-]+)', texto)

    if match:
        return match.group(1).strip()

    return None
# =========================
# EXTRAER HEADER (RUTA Y CARRETERA)
# =========================
def extract_header_info(text):
    ruta = None
    carretera = None

    # Normalizar texto fuerte
    text = re.sub(r"\s+", " ", text)

    # =========================
    # CARRETERA
    # =========================
    carretera_match = re.search(r"CARR:\s*(.*?)\s*CLAVE:", text)
    if carretera_match:
        carretera = carretera_match.group(1).strip()

    # =========================
    # RUTA (FORMA ROBUSTA)
    # =========================
    ruta = extraer_ruta(text)

    return ruta, carretera

# =========================
# EXTRACCIÓN
# =========================
def extract_viales(url):
    logger.info(f"Descargando PDF: {url}")

    response = requests.get(url, verify=False)

    data = []

    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(response.content)
        tmp.flush()

        with pdfplumber.open(tmp.name) as pdf:

            ruta = None
            carretera = None

            for page in pdf.pages:
                text = page.extract_text()

                if not text:
                    continue

                # Header
                r, c = extract_header_info(text)
                if r:
                    ruta = r
                if c:
                    carretera = c

                lines = text.split("\n")

                for line in lines:
                    line = re.sub(r"\s+", " ", line).strip()

                    match = re.match(
                        r"(.+?)\s+(\d+\.\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([-]?\d+\.\d+)\s+([-]?\d+\.\d+)",
                        line
                    )

                    if not match:
                        continue

                    try:
                        registro = {
                            "ruta": ruta,
                            "carretera": carretera,
                            "segmento": match.group(1),

                            "km": float(match.group(2)),
                            "tdpa": int(match.group(5)),

                            "A": float(match.group(7)),
                            "B": float(match.group(8)),
                            "C2": float(match.group(9)),
                            "C3": float(match.group(10)),
                            "T3S2": float(match.group(11)),
                            "T3S3": float(match.group(12)),
                            "OTROS": float(match.group(13)),

                            "lat": float(match.group(20)),
                            "lon": float(match.group(21))
                        }

                        data.append(registro)

                    except Exception as e:
                        logger.warning(f"Error parseando línea: {line}")
                        continue

    logger.info(f"Filas extraídas: {len(data)}")
    return data


# ==================================
# CARGA (MODIFICADO PARA SNOWFLAKE)
# ==================================
def load_viales(data, year):
    hook = PostgresHook(postgres_conn_id="postgres_transito")
    conn = hook.get_conn()
    cur = conn.cursor()

    # --- ESTRATEGIA ANTISALTO DE IDS ---
    # 1. Cargamos lo que ya existe en la DB a la memoria de Python
    # Esto evita que PostgreSQL intente insertar y desperdicie IDs de la secuencia
    
    def get_existing_data(table, column, key_col=None):
        cur.execute(f"SELECT {column}, id_{table} FROM dim_{table}")
        return {row[0]: row[1] for row in cur.fetchall()}

    try:
        # Pre-cargar caches
        cache_rutas = get_existing_data("ruta", "clave_ruta")
        cache_vehiculos = get_existing_data("vehiculo", "clasificacion_sct")
        
        # Cache de carreteras es especial (usamos tupla nombre, id_ruta como llave)
        cur.execute("SELECT nombre_carretera, id_ruta, id_carretera FROM dim_carretera")
        cache_carreteras = {(row[0], row[1]): row[2] for row in cur.fetchall()}

        # Asegurar Año
        cur.execute("""
            INSERT INTO dim_tiempo (anio) VALUES (%s)
            ON CONFLICT (anio) DO UPDATE SET anio = EXCLUDED.anio RETURNING id_tiempo;
        """, (year,))
        id_tiempo = cur.fetchone()[0]

        logger.info(f"🚀 Procesando {len(data)} registros para el año {year}...")

        for row in data:
            # 2. Manejo de RUTA
            nom_ruta = row["ruta"]
            if nom_ruta not in cache_rutas:
                cur.execute("INSERT INTO dim_ruta (clave_ruta) VALUES (%s) RETURNING id_ruta;", (nom_ruta,))
                cache_rutas[nom_ruta] = cur.fetchone()[0]
            id_ruta = cache_rutas[nom_ruta]

            # 3. Manejo de CARRETERA
            nom_carr = row["carretera"]
            key_carr = (nom_carr, id_ruta)
            if key_carr not in cache_carreteras:
                cur.execute("INSERT INTO dim_carretera (nombre_carretera, id_ruta) VALUES (%s, %s) RETURNING id_carretera;", key_carr)
                cache_carreteras[key_carr] = cur.fetchone()[0]
            id_carretera = cache_carreteras[key_carr]

            # 4. Manejo de UBICACIÓN
            # Aquí usamos ON CONFLICT solo para el punto final (KM/Coordenadas)
            cur.execute("""
                INSERT INTO dim_ubicacion (id_carretera, segmento_tramo, kilometro, latitud, longitud)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id_carretera, kilometro, segmento_tramo, latitud, longitud) 
                DO UPDATE SET id_carretera = EXCLUDED.id_carretera
                RETURNING id_ubicacion;
            """, (id_carretera, row["segmento"], row["km"], row["lat"], row["lon"]))
            id_ubicacion = cur.fetchone()[0]

            # 5. CARGA DE HECHOS
            for tipo in ["A", "B", "C2", "C3", "T3S2", "T3S3", "OTROS"]:
                id_veh = cache_vehiculos.get(tipo)
                if not id_veh:
                    cur.execute("INSERT INTO dim_vehiculo (clasificacion_sct) VALUES (%s) RETURNING id_vehiculo;", (tipo,))
                    id_veh = cur.fetchone()[0]
                    cache_vehiculos[tipo] = id_veh

                cur.execute("""
                    INSERT INTO fact_movilidad (id_ubicacion, id_vehiculo, id_tiempo, cantidad_vehiculos_tdpa, porcentaje_composicion)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id_ubicacion, id_vehiculo, id_tiempo)
                    DO UPDATE SET cantidad_vehiculos_tdpa = EXCLUDED.cantidad_vehiculos_tdpa;
                """, (id_ubicacion, id_veh, id_tiempo, row["tdpa"], row[tipo]))

        conn.commit()
        logger.info(f"✅ Año {year} cargado con IDs optimizados.")

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error en año {year}: {e}")
        raise
    finally:
        cur.close()
        conn.close()
