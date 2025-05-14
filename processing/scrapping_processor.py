import pandas as pd

def procesar_datos_scrapeados(lista_deptos):
    #Convertir en dataFrame
    df = pd.DataFrame(lista_deptos)

    #Eliminaremos la columna "detalle" ya que es solo para testeo de lo scrappeado
    if 'detalles' in df.columns:
        df.drop(columns=['detalles'], inplace=True)

    
    #Renombrar columnas a formato capitalizado y sin guiones bajos
    df.rename(columns={
        'precio': 'Precio',
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

    

