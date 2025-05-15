from scraping.argenprop_scraper import scrapear_paginas_argenprop
from processing.scrapping_processor import procesar_datos_scrapeados
from datetime import datetime
import pandas as pd
import os

urls_argenprop = {
    #Cada - es que en su momento (14/05/2025) no habian registros o solo 1 
   "Buenos Aires":"https://www.argenprop.com/departamentos/alquiler/la-plata-buenos-aires",
    "Catamarca": "https://www.argenprop.com/departamentos/alquiler/catamarca-capital",
    "Chaco": "https://www.argenprop.com/departamentos/alquiler/resistencia",
    "Chubut": "https://www.argenprop.com/departamentos/alquiler/rawson-chubut", # -
    "Cordoba": "https://www.argenprop.com/departamentos/alquiler/cordoba",
    "Corrientes": "https://www.argenprop.com/departamentos/alquiler/corrientes-cor",
    "Entre Rios": "https://www.argenprop.com/departamentos/alquiler/colon-entre-rios",
    "Formosa": "https://www.argenprop.com/departamentos/alquiler/formosa",
    "Jujuy": "https://www.argenprop.com/departamentos/alquiler/san-salvador-de-jujuy", # -
    "La Pampa": "https://www.argenprop.com/departamentos/alquiler/santa-rosa-la-pampa",# -
    "La Rioja": "https://www.argenprop.com/departamentos/alquiler/la-rioja-capital-la-rioja-capital", # -
    "Mendoza": "https://www.argenprop.com/departamentos/alquiler/mendoza",
    "Misiones": "https://www.argenprop.com/departamentos/alquiler/posadas",
    "Neuquen": "https://www.argenprop.com/departamentos/alquiler/neuquen",
    "Rio Negro": "https://www.argenprop.com/departamentos/alquiler/viedma", # -  o reemplazar por Roca o Brc
    "Salta": "https://www.argenprop.com/departamentos/alquiler/salta",
    "San Juan": "https://www.argenprop.com/departamentos/alquiler/san-juan", 
    "San Luis": "https://www.argenprop.com/departamentos/alquiler/san-luis",
    "Santa Cruz": "https://www.argenprop.com/departamentos/alquiler/rio-gallegos",# - 
    "Santa fe":"https://www.argenprop.com/departamentos/alquiler/santa-fe-santa-fe",
    "Santiago del estero":"https://www.argenprop.com/departamentos/alquiler/santiago-del-estero", # - 
    "Tierra del fuego": "https://www.argenprop.com/departamentos/alquiler/ushuaia-ushuaia",
    "Tucuman": "https://www.argenprop.com/departamentos/alquiler/san-miguel-de-tucuman",

    #Menciones Especiales
    "Caba": "https://www.argenprop.com/departamento-en-alquiler-en-capital-federal",
    "Rosario": 'https://www.argenprop.com/departamentos/alquiler/rosario-santa-fe',
    "Bariloche": "https://www.argenprop.com/departamentos/alquiler/bariloche-o-san-carlos-de-bariloche"
}

todos_los_registros = []
maximo_registro_por_ciudad = 50
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
