# 🏡 Alquileres-ARG

**Alquileres-ARG** es un proyecto de scraping, procesamiento y análisis de precios de alquileres en Argentina, con el objetivo de construir un dataset limpio y confiable que permita evaluar el costo de vivir en distintas ciudades del país. El análisis posterior se realiza en Power BI.

---

## 📌 Objetivos del proyecto

- Obtener precios de alquiler desde plataformas inmobiliarias (actualmente Argenprop).
- Limpiar y transformar los datos crudos.
- Imputar datos faltantes como superficie y cantidad de baños de manera inteligente.
- Convertir precios en USD a ARS utilizando la API pública de Bluelytics.
- Generar un CSV listo para análisis visual y estadístico.
- Crear dashboards informativos sobre la situación habitacional del país.

---

## 🛠️ Tecnologías utilizadas

- **Python 3.10+**
- **Pandas**, **NumPy**, **re**
- **Bluelytics API** (conversión USD a ARS)
- **Power BI** para la visualización final

---

## 🧠 Flujo del proyecto

```
[SCRAPER] --> [datasets/raw/] --> [CLEANER] --> [datasets/clean/] --> [Power BI]
```

### 1. Scraping de datos
📄 `scraping/argenprop_scraper.py`  
Extrae datos de propiedades desde Argenprop y genera un `DataFrame`.  

### 2. Procesamiento inicial
📄 `processing/scrapping_processor.py`  
Convierte los datos crudos a CSV con nombre `argenprop_YYYY-MM-DD.csv` y los guarda en `datasets/raw/`.  

### 3. Limpieza y estandarización
📄 `processing/cleaner.py`  
- Limpieza de columnas (precio, expensas, superficie, dormitorios, baños, ambientes, antigüedad).  
- Conversión de precios en USD a ARS usando [API de Bluelytics](https://api.bluelytics.com.ar/).  
- Imputación de valores faltantes de `superficie` y `baños`.  
- Eliminación de registros inconsistentes.  
- Generación de columna `valor_total = precio + expensas` y `precio_m2 = precio / superficie`.  

### 4. Dataset limpio
📄 `datasets/clean/alquileres_clean.csv`  
Contiene los datos preparados para análisis en Power BI.

---

## 🧠 Lógica de imputación y validaciones

### Imputación de superficie
- Se usa la **media** por combinación `(dormitorios, baños)` para imputar valores faltantes.
- Ejemplo de superficie mínima observada (en el momento de la limpieza):

| Dormitorios | Baños | Superficie mínima |
|-------------|-------|--------------------|
| 2           | 2     | 48 m²              |
| 3           | 2     | 70 m²              |
| 3           | 3     | 100 m²             |
| 3           | 1     | 90 m²              |

➡️ Si un inmueble tiene **3 dormitorios y solo 60 m²**, es muy probablemente **una anomalía**.  
➡️ Pero si tiene **3 dormitorios y 120 m²**, es esperable que tenga al menos 2 baños.

### Imputación de baños
- Se define `superficie_rango` usando `pd.qcut()` (cuartiles). Si falla, se hace una clasificación por `cut()` con rangos fijos.
- Se agrupan registros por `(dormitorios, superficie_rango)`.
- Se imputa `baños` faltantes con la **mediana** del grupo, para mayor robustez frente a outliers.
- Se agregan flags `banos_imputado` y `superficie_imputada`.

---

## 🧼 Validaciones y limpieza final
Se eliminan registros que:
- No tienen superficie ni dormitorios.
- Tienen superficie menor a 20 m² (parámetro configurable).

Además se validan inconsistencias como:
- Casos con más baños que dormitorios.
- Superficies inusualmente bajas con muchos dormitorios.

---

## 📂 Estructura del proyecto

```
Alquileres-ARG/
│
├── datasets/
│   ├── raw/         ← CSVs crudos del scraper
│   └── clean/       ← CSVs limpios listos para analizar
│
├── processing/
│   └── cleaner.py   ← Script principal de procesamiento
│
├── main.py          ← Punto de entrada del proceso
├── requirements.txt
├── README.md
```

---


## 🔁 Conversión de divisas

Si el precio está expresado en dólares (USD), se convierte a pesos argentinos (ARS) utilizando la **API oficial de [Bluelytics](https://api.bluelytics.com.ar/v2/latest)** para obtener la cotización blue del día.

---

## ▶️ Cómo ejecutar el proyecto

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/AgustinLago22/Alquileres-ARG.git
   cd Alquileres-ARG
   ```

2. Crear y activar el entorno virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # En Windows
   ```

3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutar el procesamiento:
   ```bash
   python main.py
   ```

---
## 📌 Consideraciones y Futuras Mejoras

Durante el desarrollo del proyecto surgieron múltiples desafíos vinculados a la calidad de los datos inmobiliarios en Argentina. Muchos registros carecen de información crítica como superficie, cantidad de baños o expensas, y otros incluyen valores evidentemente erróneos (por ejemplo, propiedades de 3 dormitorios en menos de 50 m²).

Además, en el país no existe una base centralizada ni estandarizada de información inmobiliaria, lo que complica la obtención y análisis de datos confiables. Este proyecto incorpora técnicas de imputación y validación para mejorar la calidad general del dataset, pero aún así, refleja una problemática real: la inconsistencia en los registros provistos por los usuarios o las inmobiliarias.

### 📊 Futuras mejoras

- Incorporar datos salariales promedio por provincia o ciudad (a través de fuentes como la API de RIPTE o EPH), para construir un **indicador de asequibilidad** que cruce precios de alquiler con el poder adquisitivo local. (No utilizo RIPTE al momento de hacer esto, porque siento que no es detallado para la situacion Argentina Actual)
- Agregar una capa de análisis sobre **outliers y registros irregulares** (como propiedades mal distribuidas o mal tipificadas).
- Permitir comparar entre ciudades o capitales provinciales mediante un dashboard interactivo.
- Añadir un módulo histórico para analizar la **evolución del mercado de alquileres** en el tiempo.

Este proyecto busca no solo limpiar y analizar datos, sino también ofrecer herramientas que ayuden a tomar decisiones informadas en el mercado de alquiler argentino.
---

##  Autor

**Osvaldo Agustín Lago**  
Licenciatura en Sistemas de Información  
GitHub: [AgustinLago22](https://github.com/AgustinLago22)

---

## 📃 Licencia

Este proyecto se distribuye bajo la licencia MIT.