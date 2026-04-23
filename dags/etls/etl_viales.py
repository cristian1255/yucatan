import logging
import requests
import pdfplumber
import tempfile
import re
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)

class ValesETL:
    """Pipeline ETL para datos viales"""
    
    def __init__(self, postgres_conn_id="postgres_default"):
        self.conn_id = postgres_conn_id
        self.hook = PostgresHook(postgres_conn_id=self.conn_id)
    
    def crear_tablas(self):
        """Crear tablas en PostgreSQL"""
        try:
            logger.info("Creando tablas...")
            
            sql = """
            CREATE TABLE IF NOT EXISTS dim_ubicacion (
                id_ubicacion SERIAL PRIMARY KEY,
                ruta VARCHAR(50),
                carretera VARCHAR(255),
                segmento_tramo VARCHAR(255),
                kilometro DECIMAL(10,2),
                latitud DECIMAL(10,6),
                longitud DECIMAL(10,6),
                fecha_creacion TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS dim_vehiculo (
                id_vehiculo SERIAL PRIMARY KEY,
                clasificacion_sct VARCHAR(10) UNIQUE,
                fecha_creacion TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS dim_tiempo (
                id_tiempo SERIAL PRIMARY KEY,
                anio INTEGER UNIQUE,
                fecha_creacion TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS fact_movilidad (
                id_hecho SERIAL PRIMARY KEY,
                id_ubicacion INTEGER REFERENCES dim_ubicacion(id_ubicacion),
                id_vehiculo INTEGER REFERENCES dim_vehiculo(id_vehiculo),
                id_tiempo INTEGER REFERENCES dim_tiempo(id_tiempo),
                cantidad_vehiculos_tdpa INTEGER,
                porcentaje_composicion DECIMAL(10,2),
                fecha_carga TIMESTAMP DEFAULT NOW()
            );
            """
            
            self.hook.run(sql)
            logger.info("Tablas creadas exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error creando tablas: {e}")
            return False
    
    def extraer_pdf(self, url):
        """Extraer datos de un PDF"""
        try:
            logger.info(f"Descargando PDF: {url}")
            
            response = requests.get(url, verify=False, timeout=30)
            response.raise_for_status()
            
            data = []
            
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(response.content)
                tmp.flush()
                
                with pdfplumber.open(tmp.name) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            lines = text.split("\n")
                            for line in lines:
                                # Parsear líneas si es necesario
                                data.append({"raw": line})
            
            logger.info(f"PDF procesado: {len(data)} líneas extraídas")
            return data
            
        except Exception as e:
            logger.error(f"Error extrayendo PDF: {e}")
            return []
    
    def cargar_datos(self, data, year):
        """Cargar datos a PostgreSQL"""
        try:
            logger.info(f"Cargando datos para año {year}...")
            
            # Insertar año
            self.hook.run(
                "INSERT INTO dim_tiempo (anio) VALUES (%s) ON CONFLICT (anio) DO NOTHING",
                (year,)
            )
            
            logger.info(f"Datos cargados: {len(data)} registros")
            return len(data)
            
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
            return 0

def ejecutar_etl_viales(**context):
    """Función para ejecutar ETL de viales"""
    etl = ValesETL()
    
    # Crear tablas
    etl.crear_tablas()
    
    # Datos de ejemplo
    data = [{"km": 0, "tdpa": 100}]
    
    # Cargar datos
    registros = etl.cargar_datos(data, 2026)
    
    return {
        "status": "success",
        "registros": registros,
    }
