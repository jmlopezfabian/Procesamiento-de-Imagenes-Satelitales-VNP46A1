import json
import re
import numpy as np
from datetime import datetime
from typing import Tuple, List, Optional
from models import CoordenadasPixeles
from config import RUTA_MUNICIPIOS

def normalize_municipio(municipio: str) -> str:
    """Normaliza el nombre del municipio removiendo acentos"""
    return municipio.lower().replace("á", "a").replace("é", "e")\
        .replace("í", "i").replace("ó", "o").replace("ú", "u")

def parse_date(date_str: str) -> Tuple[int, int, datetime.date]:
    """Parsea una fecha en formato dd-mm-yy y retorna año, día del año y objeto date"""
    date = datetime.strptime(date_str, "%d-%m-%y")
    return date.year, date.timetuple().tm_yday, date.date()

def load_coord_data(municipio: str, path: str) -> CoordenadasPixeles:
    """Carga las coordenadas de píxeles de un municipio desde un archivo JSON"""
    with open(path, "r") as f:
        data = json.load(f)
    return CoordenadasPixeles(**data[municipio])

def extraer_coordenadas(nombre_delegacion: str) -> Optional[np.ndarray]:
    """Extrae las coordenadas de un municipio desde el archivo de límites"""
    try:
        with open(RUTA_MUNICIPIOS, "r") as file:
            datos = json.load(file)
        
        for data in datos["features"]:
            if data["properties"]["NOMGEO"] == nombre_delegacion:
                return np.array(data["geometry"]["coordinates"][0])
        
        print(f"No se encontraron coordenadas para la delegación: {nombre_delegacion}")
        return None
    except Exception as e:
        print(f"Error al extraer coordenadas: {e}")
        return None

def left_right_coords(hdf_file) -> Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]]:
    """Extrae las coordenadas de la esquina superior izquierda e inferior derecha del archivo HDF"""
    try:
        dataset_path = "HDFEOS INFORMATION/StructMetadata.0"
        metadata = hdf_file[dataset_path][()].tobytes().decode("utf-8")

        upper_left_match = re.search(r"UpperLeftPointMtrs=\(([-\d.]+),([-\d.]+)\)", metadata)
        lower_right_match = re.search(r"LowerRightMtrs=\(([-\d.]+),([-\d.]+)\)", metadata)
        conversion = 1_000_000

        if upper_left_match and lower_right_match:
            upper_left_coords = (
                float(upper_left_match.group(1)) / conversion,
                float(upper_left_match.group(2)) / conversion,
            )
            lower_right_coords = (
                float(lower_right_match.group(1)) / conversion,
                float(lower_right_match.group(2)) / conversion,
            )
            return upper_left_coords, lower_right_coords

        print("No se pudieron extraer las coordenadas.")
        return None, None
    except Exception as e:
        print(f"Error al extraer coordenadas del archivo HDF: {e}")
        return None, None

def distancia_puntos(x: Tuple[float, float], y: Tuple[float, float]) -> float:
    """Calcula la distancia euclidiana entre dos puntos"""
    return np.sqrt((x[0]-y[0])**2 + (x[1]-y[1])**2)

def polygon_centroid(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Calcula el centroide de un polígono"""
    n = len(vertices)
    A = 0
    Cx = 0
    Cy = 0

    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        A += cross
        Cx += (x0 + x1) * cross
        Cy += (y0 + y1) * cross

    A *= 0.5
    Cx /= (6 * A)
    Cy /= (6 * A)
    return (Cx, Cy)

def es_borde(x: int, y: int, bordes: List[Tuple[int, int]]) -> bool:
    """Verifica si un punto está en el borde del polígono"""
    return (x, y) in bordes 