import os
import pandas as pd

# Ruta al directorio donde están los CSV
ruta_csvs = "datasets/raw"

# Buscar archivos que empiecen con "argenprop_" y terminen en ".csv"
archivos = [f for f in os.listdir(ruta_csvs) if f.startswith("argenprop_") and f.endswith(".csv")]

if not archivos:
    print("No se encontraron archivos CSV en datasets/raw/")
    exit()

# Ordenar por fecha (extraída del nombre del archivo) y elegir el más reciente
archivos.sort(reverse=True)
archivo_mas_reciente = archivos[0]

ruta_completa = os.path.join(ruta_csvs, archivo_mas_reciente)
print(f"Cargando archivo más reciente: {archivo_mas_reciente}")

# Leer el CSV
df = pd.read_csv(ruta_completa)

# Mostrar una vista previa
print(df)
