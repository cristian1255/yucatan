import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger("airflow.task")

def obtener_urls_sct():
    BASE = "https://micrs.sct.gob.mx"
    URL_RAIZ = BASE + "/index.php/infraestructura/direccion-general-de-servicios-tecnicos/datos-viales"

    resultados = []

    try:
        # 1. Obtener la página principal
        res = requests.get(URL_RAIZ, verify=False, timeout=30)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # ---------------------------------------------------------
        # 2. OBTENER Y ORDENAR AÑOS (Dinámico)
        # ---------------------------------------------------------
        anios_encontrados = []
        
        # Buscamos todos los enlaces que parezcan años (que contengan datos-viales/20)
        for a in soup.select("a[href*='datos-viales/20']"):
            texto = a.text.strip()
            if texto.isdigit():
                href = a.get("href")
                url_completa = BASE + href if href.startswith("/") else href
                anios_encontrados.append((int(texto), url_completa))

        # Ordenamos de mayor a menor para asegurar que los primeros sean los más nuevos
        anios_encontrados.sort(key=lambda x: x[0], reverse=True)

        # Seleccionamos los últimos 10 años disponibles en la página
        ultimos_10_anios = anios_encontrados[:10]
        
        logger.info(f"Se encontraron {len(anios_encontrados)} años. Procesando los {len(ultimos_10_anios)} más recientes.")

        # ---------------------------------------------------------
        # 3. NAVEGAR EN CADA AÑO
        # ---------------------------------------------------------
        for year, url_anio in ultimos_10_anios:
            logger.info(f"📅 Escaneando año: {year}")

            try:
                res_anio = requests.get(url_anio, verify=False, timeout=30)
                soup_anio = BeautifulSoup(res_anio.text, "html.parser")

                # Buscamos el PDF de Yucatán
                # Buscamos tanto en la clase 'download' como en cualquier link que diga 'yucat'
                links = soup_anio.find_all("a", href=True)
                
                encontrado = False
                for a in links:
                    nombre_link = a.text.lower()
                    url_pdf = a.get("href")

                    if "yucat" in nombre_link and ".pdf" in url_pdf.lower():
                        link_final = BASE + url_pdf if url_pdf.startswith("/") else url_pdf
                        
                        resultados.append({
                            "year": year,
                            "url": link_final
                        })
                        logger.info(f"✅ Enlace Yucatán {year} detectado: {link_final}")
                        encontrado = True
                        break 
                
                if not encontrado:
                    logger.warning(f"⚠️ No se encontró PDF de Yucatán para el año {year}")

            except Exception as e:
                logger.error(f"❌ Error al procesar el año {year}: {e}")
                continue

    except Exception as e:
        logger.error(f"❌ Error general en el scraper: {e}")

    return resultados
