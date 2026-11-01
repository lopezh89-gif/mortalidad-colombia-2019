# Mortalidad en Colombia 2019: observatorio interactivo

## Introducción
Aplicación web dinámica que explora registros de defunciones no fetales de Colombia en 2019 mediante Dash y Plotly, con datos del DANE y correspondencia territorial de DIVIPOLA.

## Objetivo
Examinar patrones territoriales, temporales, demográficos y de causas de muerte mediante siete visualizaciones interactivas y filtros por departamento, sexo y mes.

## Datos y metodología
Se procesaron **244.355 registros** provenientes de `Anexo1.NoFetal2019_CE_15-03-23.xlsx`; se cruzaron con `Divipola_CE_.xlsx` y `Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx`. El resultado se guarda comprimido en `data/mortalidad_2019_preparada.csv.gz`.

- Los códigos CIE-10 se agrupan por sus **primeros tres caracteres**, utilizando el catálogo para mostrar los nombres de las causas.
- La selección de agresiones usa exclusivamente el prefijo **X95** de `COD_MUERTE`, tal como solicita la guía. No representa todos los homicidios.
- El gráfico de menor mortalidad usa **conteos**, no tasas, porque no se adjuntó una base poblacional. Por ello no permite comparar el riesgo relativo entre municipios.
- El mapa representa marcadores territoriales sobre centros aproximados, no polígonos coropléticos; para un mapa coroplético estricto se necesitaría incorporar un GeoJSON departamental oficial.
- Las categorías de edad usan explícitamente la tabla `GRUPO_EDAD1` de la actividad. El panel presenta frecuencias categorizadas, equivalentes a un histograma discreto de categorías.
- `COD_DANE` conserva los ceros a la izquierda y se cruza con DIVIPOLA.
- Los resultados son descriptivos; las diferencias no demuestran causalidad ni equivalen a tasas ajustadas por población o estructura demográfica.

## Estructura
- `app.py`: app Dash, callbacks y gráficos.
- `data/mortalidad_2019_preparada.csv.gz`: datos originales transformados (se incluye para reproducir ejecución sin volver a procesar archivos de origen).
- `assets/style.css`: diseño adaptable.
- `requirements.txt`: dependencias.
- `render.yaml`: configuración para Render.
- `screenshots/`: capturas por completar después de ejecutar la aplicación.

## Requisitos y software
Python 3.10+; Dash, Plotly, pandas, numpy y Gunicorn (versiones compatibles indicadas en requirements.txt). IDE recomendado: VS Code. Control de versiones: Git/GitHub. PaaS: Render.

## Instalación
```bash
git clone URL_DEL_REPOSITORIO
cd mortalidad_colombia_2019
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```
Abrir `http://127.0.0.1:8050`.

## Despliegue en Render
1. Crear repositorio de GitHub y subir **todos** los archivos y la carpeta `data/`.
2. Abrir Render > New > Web Service > conectar GitHub > seleccionar el repositorio.
3. Seleccionar Python, `pip install -r requirements.txt` para build y `gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 120` como start.
4. Elegir servicio disponible y desplegar; `render.yaml` permite configuración mediante Blueprint.
5. Verificar siete gráficos, filtros y funcionamiento de la URL pública.

## Visualizaciones, interpretación y hallazgos
1. **Mapa territorial:** permite observar la concentración de registros por departamento. Los valores representan números absolutos, no tasas.
2. **Serie mensual:** muestra la distribución de defunciones a lo largo de los doce meses; cualquier máximo o mínimo debe examinarse después de filtrar.
3. **Cinco municipios X95:** ordena las localidades según agresiones por armas de fuego correspondientes a X95. La base contiene **9.273** registros X95 a escala nacional.
4. **Diez municipios con menos defunciones:** representa los registros más bajos entre municipios observados; no se debe afirmar que sean los municipios con menor riesgo de morir.
5. **Principales causas:** el grupo CIE-10 `I21` (infarto agudo del miocardio) concentra **35.323** registros, seguido de `J44` (otras enfermedades pulmonares obstructivas crónicas) con **15.804**.
6. **Barras por sexo:** permite comparar volúmenes y composición de defunciones por departamento, sin ajuste por población.
7. **Grupos de edad:** facilita identificar en qué etapas de vida se concentra el número de defunciones registradas.

### Capturas de pantalla
Después de iniciar la app, incorporar imágenes en `screenshots/` y referenciarlas en esta sección. Para evitar inventar evidencia, no se incluyen capturas simuladas.

## Referencias
Departamento Administrativo Nacional de Estadística (DANE). (2019). *Estadísticas vitales: defunciones no fetales 2019* [Base de datos].

DANE. *División Político-Administrativa (DIVIPOLA)* [Catálogo].

Catálogo CIE-10 suministrado con la actividad, actualización 8 de febrero de 2021.

## Autoría y entrega
Estudiante: Jonnathan López Hurtado. Periodo: 2026-II. Completar los demás integrantes, si corresponde. Cada integrante entrega individualmente los enlaces del repositorio GitHub y la aplicación desplegada.
