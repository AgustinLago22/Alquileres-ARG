import requests
from bs4 import BeautifulSoup
import re  # Importamos el módulo de expresiones regulares

def scrapear_paginas_argenprop(base_url,ciudad, max_registros=20):
    registros = []
    pagina = 1

    while len(registros) < max_registros: # Nos va a permitir poner un tope de registros
        url = f"{base_url}-pagina-{pagina}"
        print(f"Scrapeando página {pagina}: {url}")
        datos_pagina = scrapear_argenprop(url,ciudad)

        if not datos_pagina:  # No pasa nada si no llega a 100, lo importante es tener datos
            print("No se encontraron más resultados.")
            break

        registros.extend(datos_pagina)
        pagina += 1

    return registros[:max_registros]


import re

def obtener_precio(depto):
    precio_tag = depto.find('p', {'class': 'card__price'})
    if precio_tag:
        precio = precio_tag.text.strip()
        if "Consultar precio" in precio:
            return "No disponible", "No disponible"  # Si no hay precio disponible

        # Verificamos si existe un "+" en el precio para dividirlo
        if "+" in precio:
            # Dividimos en dos partes: precio y expensas
            partes = precio.split(" + ")
            precio_alquiler = partes[0].strip()  # El primer segmento es el precio
            expensas = partes[1].replace("expensas", "").strip()  # El segundo es las expensas

            # Limpiamos el formato, eliminando los puntos de miles y convirtiendo a número
            precio_alquiler = int(precio_alquiler.replace('.', '').replace('$', '').strip())
            expensas = int(expensas.replace('.', '').replace('$', '').strip()) if expensas else "No disponible"
        else:
            # Si no hay "+" en el precio, solo devolvemos el precio de alquiler
            precio_alquiler = int(precio.replace('.', '').replace('$', '').strip())
            expensas = "No disponible"  # Si no hay expensas, marcamos como No disponible

        return precio_alquiler, expensas

    return "No disponible", "No disponible"  # Si no encontramos el precio, devolvemos "No disponible"



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


def scrapear_argenprop(url,ciudad):
    departamentos = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        deptos = soup.find_all('div', class_='card__details-box')

        for depto in deptos:
            precio, expensas = obtener_precio(depto)  # Obtenemos el precio y expensas
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
