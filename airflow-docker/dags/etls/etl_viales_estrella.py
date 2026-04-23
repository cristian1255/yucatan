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


# =========================
# CARGA
# =========================
def load_viales(data, year):
    hook = PostgresHook(postgres_conn_id="postgres_viales")

    # Tiempo: Este se queda igual (necesitamos el ID del año)
    id_tiempo = hook.get_first("""
        INSERT INTO dim_tiempo (anio)
        VALUES (%s)
        ON CONFLICT (anio)
        DO UPDATE SET anio = EXCLUDED.anio
        RETURNING id_tiempo;
    """, (year,))[0]

    for row in data:
        try:
            # =========================
            # UBICACION (INSERT DIRECTO)
            # =========================
            # Como ya NO EXISTE la restricción UNIQUE en la DB, 
            # este INSERT aceptará todo, incluso si la carretera/km se repiten.
            id_ubicacion = hook.get_first("""
                INSERT INTO dim_ubicacion (
                    ruta, carretera, segmento_tramo, kilometro, latitud, longitud
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_ubicacion;
            """, (
                row["ruta"],
                row["carretera"],
                row["segmento"],
                row["km"],
                row["lat"],
                row["lon"]
            ))[0]

            # =========================
            # VEHICULOS + FACT
            # =========================
            for clasif in ["A", "B", "C2", "C3", "T3S2", "T3S3", "OTROS"]:

                id_vehiculo = hook.get_first("""
                    INSERT INTO dim_vehiculo (clasificacion_sct)
                    VALUES (%s)
                    ON CONFLICT (clasificacion_sct)
                    DO UPDATE SET clasificacion_sct = EXCLUDED.clasificacion_sct
                    RETURNING id_vehiculo;
                """, (clasif,))[0]

                # Insertamos en la tabla de hechos usando el ID único de esta ubicación
                hook.run("""
                    INSERT INTO fact_movilidad
                    (
                        id_ubicacion,
                        id_vehiculo,
                        id_tiempo,
                        cantidad_vehiculos_tdpa,
                        porcentaje_composicion
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """, parameters=(
                    id_ubicacion,
                    id_vehiculo,
                    id_tiempo,
                    row["tdpa"],
                    row[clasif]
                ))

        except Exception as e:
            logger.error(f"Fallo en fila {row.get('segmento')} (KM {row.get('km')}): {e}")
            continue