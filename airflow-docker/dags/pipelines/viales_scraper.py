import requests
from bs4 import BeautifulSoup

def obtener_urls_sct():

    BASE = "https://micrs.sct.gob.mx"
    URL = BASE + "/index.php/infraestructura/direccion-general-de-servicios-tecnicos/datos-viales"

    resultados = []

    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    # -------------------------
    # 1. OBTENER AÑOS
    # -------------------------
    anios = []

    for a in soup.select("a[href*='datos-viales/20']"):
        texto = a.text.strip()
        if texto.isdigit():
            anios.append((texto, BASE + a.get("href")))

    # -------------------------
    # 2. ENTRAR A CADA AÑO
    # -------------------------
    for year, url_anio in anios[:5]:  # solo 5

        print(f"📅 {year}")

        res_anio = requests.get(url_anio)
        soup_anio = BeautifulSoup(res_anio.text, "html.parser")

        # -------------------------
        # 3. BUSCAR YUCATÁN
        # -------------------------
        for a in soup_anio.select("a.download"):

            if "yucat" in a.text.lower():
                resultados.append({
                    "year": int(year),
                    "url": BASE + a.get("href")
                })
                print(f"✅ {BASE + a.get('href')}")
                break

    return resultados