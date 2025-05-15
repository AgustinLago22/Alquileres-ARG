import requests
from bs4 import BeautifulSoup
import re  # Importamos el módulo de expresiones regulares
import requests
def scrapear_paginas_argenprop(base_url, ciudad, max_registros):
    registros = []
    pagina = 1
    datos_anteriores = None
    dolarhoy = obtener_cotizacion_dolar()

    while len(registros) < max_registros:
        if pagina == 1:
            url = base_url
        else:
            url = f"{base_url}?pagina-{pagina}" # Cuando se pagina la pagina cambia a este formato (https://www.argenprop.com/departamentos/alquiler/resistencia) base_url?pagina-2

        print(f"Scrapeando página {pagina}: {url}")
        datos_pagina = scrapear_argenprop(url, ciudad,dolarhoy)

        if not datos_pagina:
            print("No se encontraron más resultados.")
            break

        # Comparamos solo las direcciones para detectar repetición
        direcciones_actual = [d['direccion'] for d in datos_pagina]
        direcciones_anteriores = [d['direccion'] for d in datos_anteriores] if datos_anteriores else []

        if datos_anteriores and direcciones_actual == direcciones_anteriores:
            print("Página repetida detectada. Fin de la paginación.")
            break

        registros.extend(datos_pagina)
        datos_anteriores = datos_pagina
        pagina += 1

    return registros[:max_registros]



def scrapear_argenprop(url,ciudad,dolarhoy):
    departamentos = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        deptos = soup.find_all('div', class_='card__details-box')

        for depto in deptos:
            precio, expensas = obtener_precio(depto,dolarhoy)  # Obtenemos el precio y expensas
            direccion = obtener_direccion(depto)
            detalles = obtener_detalles(depto)

            depto_info = {
                'precio': precio,
                'expensas': expensas, 
                'direccion': direccion,
                'detalles': detalles,  # No es necesario, solo es para testeo en main y ver que obtiene
                'superficie_cubierta': detalles.get('superficie_cubierta', 'No disponible'),
                'dormitorios': detalles.get('dormitorios', 'No disponible'),
                'banos': detalles.get('banos', 'No disponible'),
                'antiguedad': detalles.get('antiguedad', 'No disponible'),
                'ambientes': detalles.get('ambientes', 'No disponible'),
                'fuente': 'argenprop',
                'ciudad': ciudad
            }
            departamentos.append(depto_info)

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la página: {e}")

    return departamentos




def obtener_cotizacion_dolar():
    url= "https://api.bluelytics.com.ar/v2/latest"  # Api para obtener cotizacion dolar
    try:
        response= requests.get(url)
        data = response.json()
        oficial= data['oficial']['value_sell'] #Como se elimino el cepo, tomamos el dolar oficial.
        return oficial
    except Exception as e:
        print("Error al obtener cotizacion", e)
        return None     



def obtener_precio(depto, dolarhoy):
    precio_tag = depto.find('p', {'class': 'card__price'})
    if not precio_tag:
        return "No disponible", "No disponible"

    texto = " ".join(precio_tag.text.strip().split())

    if "Consultar precio" in texto:
        return "No disponible", "No disponible"

    # Determinar si es en USD
    es_usd = "USD" in texto
    texto = texto.replace("USD", "").replace("$", "").strip()

    # Separar expensas si hay
    if "+" in texto:
        partes = texto.split("+")
        alquiler_str = partes[0].strip()
        expensas_str = partes[1].replace("expensas", "").replace("$", "").strip()
    else:
        alquiler_str = texto
        expensas_str = None

    try:
        precio_alquiler = int(alquiler_str.replace(".", ""))
    except ValueError:
        precio_alquiler = "No disponible"

    # Si el precio era en USD, convertir
    if es_usd:
        precio_alquiler = round(precio_alquiler * dolarhoy)

    try:
        expensas = int(expensas_str.replace(".", "")) if expensas_str else "No disponible"
    except ValueError:
        expensas = "No disponible"

    return precio_alquiler, expensas



def obtener_direccion(depto):
    direccion_tag = depto.find('p', {'class': 'card__address'})
    return direccion_tag.text.strip() if direccion_tag else "No disponible"




def obtener_detalles(depto):
    detalles = {}
    detalle_tags = depto.find_all('li')
    for detalle in detalle_tags:
        icono = detalle.find('i')
        if icono:
            icono_class = icono.get('class', [])
            span = detalle.find('span')
            valor = span.text.strip() if span else "No disponible"

            if 'icono-superficie_cubierta' in icono_class:
                detalles['superficie_cubierta'] = valor
            elif 'icono-cantidad_dormitorios' in icono_class:
                detalles['dormitorios'] = valor
            elif 'icono-antiguedad' in icono_class:
                detalles['antiguedad'] = valor
            elif 'icono-cantidad_banos' in icono_class:
                detalles['banos'] = valor
            elif 'icono-cantidad_ambientes' in icono_class:
                detalles['ambientes'] = valor
    return detalles

