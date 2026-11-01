
import json
from pathlib import Path

import plotly.express as px

ARCHIVO = (
    Path(__file__).resolve().parent
    / "data"
    / "col_departamentos_inset_nacional.geojson"
)


def construir_mapa(decesos):
    por_dpto = (
        decesos.assign(
            COD_DEP_MAPA=decesos[
                "COD_DEPARTAMENTO"
            ].astype(str).str.zfill(2)
        )
        .groupby("COD_DEP_MAPA", as_index=False)
        .agg(
            Defunciones=("COD_DANE", "size"),
            Departamento=("DEPARTAMENTO", "first")
        )
    )

    if por_dpto.empty:
        return px.scatter(
            title="Sin datos para los filtros seleccionados"
        )

    try:
        with open(ARCHIVO, encoding="utf-8") as archivo:
            geojson = json.load(archivo)

        if not geojson.get("features"):
            raise ValueError("GeoJSON sin geometrías")

        figura = px.choropleth_map(
            por_dpto,
            geojson=geojson,
            locations="COD_DEP_MAPA",
            featureidkey="properties.divipola_dep",
            color="Defunciones",
            hover_name="Departamento",
            color_continuous_scale="Blues",
            map_style="carto-positron",
            center={"lat": 4.6, "lon": -74.1},
            zoom=3.4,
            opacity=0.85,
            height=490,
            labels={
                "Defunciones": "Defunciones registradas"
            }
        )

        figura.update_layout(
            margin=dict(t=0, b=0, l=0, r=0)
        )

        return figura

    except Exception as error:
        print("Error cartografico:", repr(error))

        figura = px.scatter(
            title="No se pudo cargar el mapa departamental"
        )
        figura.add_annotation(
            text="Verificar el archivo GeoJSON en data/",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False
        )
        return figura
