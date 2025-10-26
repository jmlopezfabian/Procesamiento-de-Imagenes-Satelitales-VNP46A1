import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import seaborn as sns
import json
from utils import polygon_centroid
from config import RUTA_MUNICIPIOS
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union


from geopy.distance import geodesic

def distancia_puntos(x: tuple[float, float], y: tuple[float, float]) -> float:
    """
    Calcula la distancia geodésica (en kilómetros) entre dos puntos dados como (lon, lat).
    """
    p1 = (x[1], x[0])
    p2 = (y[1], y[0])
    distancia = geodesic(p1, p2).kilometers
    return distancia


with open(RUTA_MUNICIPIOS, "r") as file:
    datos = json.load(file)

colores = sns.color_palette("Set1", 16)

for i, municipio in enumerate(datos["features"]):
    if municipio["properties"]["NOMGEO"] not in ["Monterrey", "Oaxaca de Juárez"]:
        coordenadas = municipio["geometry"]["coordinates"][0]
        centroide = polygon_centroid(coordenadas)
        plt.plot([c[0] for c in coordenadas], [c[1] for c in coordenadas],
                 color=colores[i], label=municipio["properties"]["NOMGEO"], linewidth=1)
        plt.scatter(centroide[0], centroide[1], color=colores[i], s=20)


municipios_borde = [
    "Gustavo A. Madero", "Azcapotzalco", "Miguel Hidalgo", "Cuajimalpa de Morelos",
    "La Magdalena Contreras", "Tlalpan", "Milpa Alta", "Tláhuac",
    "Iztapalapa", "Iztacalco", "Venustiano Carranza", "Álvaro Obregón"
]

poligonos = [Polygon(m["geometry"]["coordinates"][0])
             for m in datos["features"]
             if m["properties"]["NOMGEO"] in municipios_borde]

borde_cdmx = unary_union(poligonos)

x, y = borde_cdmx.exterior.xy
plt.plot(x, y, color='black', linewidth=2, label="Borde CDMX")
plt.axis("equal")

centroide_cdmx = polygon_centroid(list(zip(x, y)))

plt.scatter(centroide_cdmx[0], centroide_cdmx[1],
            color='red', s=200, edgecolor='black', zorder=5, label="Centroide CDMX")

distancias_data = []

for i, municipio in enumerate(datos["features"]):
    if municipio["properties"]["NOMGEO"] not in ["Monterrey", "Oaxaca de Juárez"]:
        coordenadas = municipio["geometry"]["coordinates"][0]
        centroide = polygon_centroid(coordenadas)
        # Línea desde municipio al centro de CDMX
        plt.plot([centroide[0], centroide_cdmx[0]],
                 [centroide[1], centroide_cdmx[1]],
                 color='gray', linestyle='--', linewidth=0.8, alpha=0.7)

        # Distancia
        distancia = distancia_puntos(centroide, centroide_cdmx)
        distancias_data.append({
            'Municipio': municipio['properties']['NOMGEO'],
            'Distancia_km': distancia
        })
        print(f"La distancia entre el centroide de {municipio['properties']['NOMGEO']} y el centroide de la CDMX es {distancia:.4f}")

df_distancias = pd.DataFrame(distancias_data)
df_distancias.to_csv('../data/distancias_centroide_cdmx.csv', index=False)

plt.legend()
plt.title("Centroide de CDMX y centroides de alcaldias")
plt.show()
