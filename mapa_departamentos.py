"""Mapa coroplético por departamentos de Colombia, usando una capa pública IDEAM.

Fuente cartográfica: IDEAM, servicio Entidades_Territoriales / FeatureServer/4.
La información temática corresponde a registros DANE 2019.
"""
import json
from functools import lru_cache
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd
import plotly.express as px

URL = 'https://visualizador.ideam.gov.co/gisserver/rest/services/Entidades_Territoriales/FeatureServer/4/query'

@lru_cache(maxsize=1)
def limites_departamentales():
    parametros = {
        'where': '1=1', 'outFields': 'cod_dane,nom_dpto',
        'returnGeometry': 'true', 'outSR': '4326', 'f': 'geojson'
    }
    peticion = Request(URL + '?' + urlencode(parametros), headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(peticion, timeout=12) as respuesta:
        geometria = json.load(respuesta)
    if not geometria.get('features'):
        raise ValueError('La fuente cartográfica no devolvió departamentos')
    for feature in geometria['features']:
        codigo = str(feature['properties'].get('cod_dane', '')).zfill(2)
        feature['properties']['cod_dane'] = codigo
        feature['id'] = codigo
    return geometria


def construir_mapa(decesos):
    """Retorna un mapa coroplético con el total de casos por departamento.

    Si la fuente geográfica falla, presenta una advertencia visible, no cifras inventadas.
    """
    por_dpto = (decesos.assign(COD_DEP_MAPA=decesos['COD_DEPARTAMENTO'].astype(str).str.zfill(2))
                .groupby('COD_DEP_MAPA', as_index=False)
                .agg(Defunciones=('COD_DANE', 'size'), Departamento=('DEPARTAMENTO', 'first')))
    if por_dpto.empty:
        figura = px.scatter(title='Sin defunciones para los filtros seleccionados')
        return figura
    try:
        geojson = limites_departamentales()
        figura = px.choropleth_map(
            por_dpto, geojson=geojson, locations='COD_DEP_MAPA',
            featureidkey='properties.cod_dane', color='Defunciones',
            hover_name='Departamento', hover_data={'COD_DEP_MAPA': False},
            color_continuous_scale='Blues',
            center={'lat': 4.6, 'lon': -74.1}, zoom=3.5,
            map_style='carto-positron', opacity=0.8, height=490,
            labels={'Defunciones': 'Defunciones registradas'}
        )
        figura.update_traces(marker_line_width=0.6, marker_line_color='white')
        figura.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        return figura
    except Exception as exc:
        # La plataforma no debe mostrar un mapa erróneo si falla la fuente externa.
        figura = px.scatter(title='No se pudo cargar la cartografía departamental')
        figura.add_annotation(text='La fuente geográfica oficial no está disponible. Intenta actualizar.',
                              x=0.5, y=0.5, xref='paper', yref='paper', showarrow=False)
        print('Error cartográfico:', repr(exc))
        return figura
