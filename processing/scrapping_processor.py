import pandas as pd
import os
from datetime import datetime

def procesar_datos_scrapeados(lista_deptos):
    #Convertir en dataFrame
    df = pd.DataFrame(lista_deptos)

    #Eliminaremos la columna "detalle" ya que es solo para testeo de lo scrappeado
    if 'detalles' in df.columns:
        df.drop(columns=['detalles'], inplace=True)

    
    #Renombrar columnas a formato capitalizado y sin guiones bajos
    #No es necesario, solo es para practicar la limpieza
    df.rename(columns={
       'precio': 'precio',
        'direccion': 'Direccion',
        'expensas' : 'Expensas',
        'superficie_cubierta': 'Superficie',
        'dormitorios': 'Dormitorios',
        'banos': 'Banos',
        'antiguedad': 'Antiguedad',
        'ambientes': 'Ambientes',
        'fuente': 'Fuente'
    }, inplace=True)
    return df
    
def guardar_datos_scrapeados(df):
    output_dir = "datasets/raw"
    os.makedirs(output_dir, exist_ok=True)
    fecha = datetime.now().strftime("%Y-%m-%d")
    ruta_csv = os.path.join(output_dir, f"argenprop_{fecha}.csv")
    df.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
    print(f"\n Datos guardados en: {ruta_csv}")
    

