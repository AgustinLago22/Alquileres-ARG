import os
import glob
import re
from datetime import datetime
import pandas as pd
import numpy as np

def obtener_ultimo_csv():
    carpeta = 'datasets/raw/'
    archivos = glob.glob(os.path.join(carpeta, 'argenprop_*.csv'))
    if not archivos:
        raise FileNotFoundError("No se encontraron archivos en datasets/raw/")
    archivos_ordenados = sorted(
        archivos,
        key=lambda x: datetime.strptime(os.path.basename(x).split('_')[1].split('.')[0], "%Y-%m-%d"),
        reverse=True
    )
    return archivos_ordenados[0]

def limpiar_monto(valor):
    if pd.isna(valor):
        return np.nan
    if isinstance(valor, str) and valor.lower() == "no disponible":
        return np.nan
    return float(valor)

def extraer_numero(texto):
    if pd.isna(texto):
        return None
    match = re.search(r'\d+',str(texto))
    return int(match.group()) if match else None


def limpiar_superficie(texto):
    if pd.isna(texto):
        return None
    match = re.search(r'\d+',str(texto))
    return int(match.group()) if match else None

def procesar_antiguedad(valor):
    if pd.isna(valor):
        return None
    valor = str(valor).lower()
    if valor == 'a estrenar':
        valor = 0
    match = re.search(r'\d+', str(valor))
    return int(match.group())if match else None
    

transformadores = {
    'precio': limpiar_monto,
    'expensas': limpiar_monto,
    'superficie' : limpiar_superficie,
    'dormitorios': extraer_numero,
    'banos': extraer_numero,
    'ambientes': extraer_numero,
    'antiguedad': procesar_antiguedad,
}


def limpiar_dataset(df):
    df.columns = df.columns.str.strip().str.lower()
    df.replace("No disponible",pd.NA, inplace=True)

    transformadores = {
    'precio': limpiar_monto,
    'expensas': limpiar_monto,
    'superficie' : limpiar_superficie,
    'dormitorios': extraer_numero,
    'banos': extraer_numero,
    'ambientes': extraer_numero,
    'antiguedad': procesar_antiguedad,
    }

    #Aplicar funciones 
    for columna, funcion in transformadores.items():
        if columna in df.columns:
            df[columna] = df[columna].apply(funcion)

    #Eliminaremos duplicados y los que no tengan precio
    df.drop_duplicates(inplace=True)
    df.dropna(subset=['precio'], inplace=True)
    df['valor_total'] = df['precio'] + df['expensas'].fillna(0) #Agregamos el fillna sin implace para no reemplazar los nulls por ceros para consistencia del dataframe

    #Forzar el casteo de float -> Int
    df['superficie'] = df['superficie'].astype("Int64")
    df['dormitorios'] = df['dormitorios'].astype("Int64")
    df['superficie'] = df['superficie'].astype("Int64")
    df['banos'] = df['banos'].astype("Int64")
    df['antiguedad'] = df['antiguedad'].astype("Int64")
    df['ambientes'] = df['ambientes'].astype("Int64")
    df['ambientes'] = df['ambientes'].astype("Int64")


    return df


def eliminar_superficies_minimas(df,umbral=20):
    cond = (df['superficie'].isna()) | (df['superficie'] > umbral)
    return df[cond].copy()



#02/07/2025
#Para hacer el dataframe mas completo, agregaremos valor a los Nan en base a estadisticas del mismo dataframe.
#El valor minimo encontrado para tener 2 dormitorios y 2 banos es de 48 metros cuadrados
#El valor minimo encontrado para 3 dormitorios y 2 banos es de 70
#El valor minimo encontrado para 3 dormitorios y 3 banos es de 100 (aun que tengo 3 registros con 101 ,105 y 105 metros con 2 dormitorios)
#Tengo un valor de 3 dormitorios y 1 bano con 90 de superficie.
def obtener_estadisticas_superficie(df):
    df.dropna(subset=['superficie','dormitorios','banos']).copy() #Eliminar filas de NaN en esas 3 columnas

    #Convertimos en int

    stats = (
        df.groupby(['dormitorios','banos'])['superficie']  # Agrupar los registros por combinacion ej 2 dor 1 bano y seleccionamos la columna de superficie para calcular
        .agg(['count','mean','median','min','max'])  # Por cada grupo dorm/bano calcular Cuanto, promedio, mediana , v.min y v.max
        .round()  #redondeamos al entero mas proximo
        .reset_index() #Volvemos a columnas normales
    )
    return stats



def llenar_superficie(df,stats_df):
     
    #Imputa valores faltantes en la columna 'superficie' utilizando la media o mediana
    #por grupo de (dormitorios, banos), según el DataFrame de estadísticas.
    
    #- df: DataFrame original con posibles valores NaN en 'superficie'
    #- stats_df: tabla generada con 'obtener_estadisticas_superficie'
    #- metodo: 'mean' o 'median', según qué estadística usar para imputar

    #Devuelve el DataFrame modificado con la columna 'superficie_fue_imputada'
    #indicando si se imputó o no.
    metodo='mean'
    df['superficie_imputada'] = False


    for _, row in stats_df.iterrows(): #_ variable desechable
        dorm= row['dormitorios']
        bano= row['banos']
        valor = row[metodo]

        cond=(
        df['superficie'].isna()&
        (df['dormitorios']==dorm)&
        (df['banos']==bano)
        )
        df.loc[cond,'superficie'] =valor
        df.loc [cond,'superficie_imputada'] = True

    return df

def deter_rangos_superficie(df):
    #Agregar una columna de rangos de superficie basada en cuantilacion -> En este caso, haremos por Cuartiles
    n_rangos = 4

    try:
        df['superficie_rango'] = pd.qcut(
            df['superficie'],
            q=n_rangos,
            duplicates='drop'
        )
    except ValueError:
        # Si qcut falla, usar cortes fijos como backup
        df['superficie_rango'] = pd.cut(
            df['superficie'],
            bins=[0, 50, 70, 90, 110, df['superficie'].max() + 1],
            labels=['0-50', '51-70', '71-90', '91-110', '110+']
        )

    return df


def obtener_estadisticas_banos(df):
    stats =(
        df.dropna(subset=['banos','dormitorios','superficie_rango']) #Sacar nulos
        .groupby(['dormitorios','superficie_rango'],observed=False)['banos'] #observed para que no Salga un warning de pandas -> Agrupa las combinaciones de dormitorios y superficie_rango y calcula en base a banos
        .agg(['count','mean','median','min','max']) #Se agregan otras estadisticas por si necesitan pruebas de algo
        .round()
        .reset_index()
    )
    return stats

def llenar_banos(df,stats):
    metodo='median'
    df=df.copy()
    df['banos_imputado'] = False

    for _, row in stats.iterrows():
        dorm= row['dormitorios']
        rango= row['superficie_rango']
        valor = row[metodo]

        cond =  (
        df['banos'].isna() &
        (df['dormitorios'] == dorm) &
        (df['superficie_rango'] == rango)
        )
        df.loc[cond,'banos']=valor
        df.loc[cond,'banos_imputado'] =True

    return df

def eliminar_inconsistentes(df):
     # Vamos a eliminar registros que no tengan superficie
    cond_superficie = df['superficie'].isna()
    
    # También eliminamos precios mayores a 5 millones por temas de venta en seccion de alquileres.
    cond_precio = df['precio'] > 10_000_000

    # Combinamos ambas condiciones con OR y eliminamos esos registros
    cond = cond_superficie | cond_precio
    df = df[~cond].copy()  # ~ es operador lógico de NOT

    return df

def validar_datos(df):
    print("\n VALIDACIÓN POST-LIMPIEZA\n")

    # 1. Conteo de valores imputados
    sup_imp = df['superficie_imputada'].sum() if 'superficie_imputada' in df.columns else 0
    ban_imp = df['banos_imputado'].sum() if 'banos_imputado' in df.columns else 0
    print(f"  Superficie imputada: {sup_imp} registros")
    print(f"  Baños imputados:     {ban_imp} registros")

    # 2. Distribución de valores imputados
    if sup_imp > 0:
        print("\n Distribución de superficie imputada:")
        print(df[df['superficie_imputada'] == True]['superficie'].value_counts().head(5))

    if ban_imp > 0:
        print("\n Distribución de baños imputados:")
        print(df[df['banos_imputado'] == True]['banos'].value_counts().head(5))

    # 3. Comparación con no imputados
    print("\n Distribución de baños en registros NO imputados:")
    print(df[df['banos_imputado'] == False]['banos'].value_counts().head(5))

    # 4. Chequeo de inconsistencias lógicas
    print("\nCasos con baños > dormitorios:")
    inconsistentes = df[(df['banos'] > df['dormitorios']) & df['banos'].notna() & df['dormitorios'].notna()]
    print(inconsistentes[['dormitorios', 'banos', 'superficie']].head())

    print("\n Casos con superficie muy baja y muchos dormitorios:")
    extremos = df[(df['superficie'] < 25) & (df['dormitorios'] >= 2)]
    print(extremos[['dormitorios', 'superficie', 'banos']].head())

    print("\nValidación finalizada.\n")

def guardar_datos_limpios(df,archivo):
    ruta_salida = os.path.join('datasets/clean','alquileres_clean.csv')
    df.to_csv(ruta_salida, index=False)
    

def cleaner():
    archivo = obtener_ultimo_csv()
    print(f"Limpieza en curso: {archivo}")
    df= pd.read_csv(archivo)
    #Limpieza donde se limpian los datos y se aplican los tipos de datos correspondientes
    df = limpiar_dataset(df)
    #Imputacion de Superficies en base a banos/dormitorios
    df = eliminar_superficies_minimas(df)#eliminacion de outliers
    stats = obtener_estadisticas_superficie(df)
    df = llenar_superficie(df, stats) #Utilizamos el estadistico media ya que refleja bien el tamano promedio de cada grupo y los outliers no distorsionan demasiado
    
    #Imputacion de Banos
    df= deter_rangos_superficie(df)
    stats = obtener_estadisticas_banos(df)
    #Imputa a los valores nulos que cumplen la condicion proveniente de stats
    df=  llenar_banos(df,stats) # Utilizamos el estadistico mediana 

    #print("Despues de funcion llenar Banos", df['banos'].isna().sum())
    #print(df[df['superficie_imputada'] == True][['dormitorios', 'banos', 'superficie']])
    #print(df[df['banos_imputado'] == True][['dormitorios', 'superficie', 'banos']])

    #Elimina filas sin Banos ni Dormitorios, Elimina columna "ambientes" ya que al momento es redudante por falta de datos
    df= eliminar_inconsistentes(df)

    #validar_datos(df)

    # Guardar en datasets/clean con mismo nombre, prefijo clean_
    guardar_datos_limpios(df,archivo)

