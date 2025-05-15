from scraping.argenprop_scraper import scrapear_paginas_argenprop
from processing.scrapping_processor import procesar_datos_scrapeados
from datetime import datetime
import pandas as pd
import os

urls_argenprop = {
    #Cada - es que en su momento (14/05/2025) no habian registros o solo 1 
   
    "Corrientes": "https://www.argenprop.com/departamentos/alquiler/la-plata-buenos-aires?solo-ver-dolares",
   
}

todos_los_registros = []
maximo_registro_por_ciudad =20
for ciudad, url in urls_argenprop.items():
    print(f"\nScrapeando: {ciudad.upper()}")
    registros = scrapear_paginas_argenprop(url,ciudad,max_registros=maximo_registro_por_ciudad)
    for r in registros:
        r["ciudad"] = ciudad  # Añadimos ciudad para identificar después
    todos_los_registros.extend(registros)

# Procesamiento
df = procesar_datos_scrapeados(todos_los_registros)

# Guardado
output_dir = "datasets/raw"
os.makedirs(output_dir, exist_ok=True)
fecha = datetime.now().strftime("%Y-%m-%d")
ruta_csv = os.path.join(output_dir, f"argenprop_{fecha}.csv")
df.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
print(f"\n Datos guardados en: {ruta_csv}")
