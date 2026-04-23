import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def obtener_urls_sct():
    """Obtener URLs de PDFs desde SCT"""
    try:
        BASE = "https://micrs.sct.gob.mx"
        URL = BASE + "/index.php/infraestructura/direccion-general-de-servicios-tecnicos/datos-viales"
        
        logger.info("Conectando a SCT...")
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Buscar años
        años = []
        for a in soup.select("a[href*='datos-viales/20']"):
            texto = a.text.strip()
            if texto.isdigit():
                años.append((texto, BASE + a.get("href")))
        
        logger.info(f"Años encontrados: {len(años)}")
        
        # Por cada año, buscar Yucatán
        resultados = []
        for year, url_anio in años[:5]:  # Últimos 5 años
            try:
                response_anio = requests.get(url_anio, timeout=10)
                response_anio.raise_for_status()
                
                soup_anio = BeautifulSoup(response_anio.text, "html.parser")
                
                for a in soup_anio.select("a.download"):
                    if "yucat" in a.text.lower():
                        pdf_url = BASE + a.get("href")
                        resultados.append({
                            "year": int(year),
                            "url": pdf_url
                        })
                        logger.info(f"Encontrado: Yucatán {year}")
                        break
            except Exception as e:
                logger.warning(f"Error procesando año {year}: {e}")
                continue
        
        logger.info(f"Total URLs encontradas: {len(resultados)}")
        return resultados
        
    except Exception as e:
        logger.error(f"Error en scraper: {e}")
        return []
