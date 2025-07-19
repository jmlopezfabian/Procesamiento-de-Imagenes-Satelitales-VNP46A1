import os
import h5py
import numpy as np
import json
import matplotlib.pyplot as plt
import pandas as pd
from .config import IMAGE_PATH, RUTA_MUNICIPIOS
from .utils import parse_date
from .downloader import find_file, download_file
from .geometry import left_right_coords, polygon_centroid
from .processing import recortar_imagen

class SatelliteImages:
    def __init__(self, municipio):
        self.municipio = municipio

    def extraer_coordenadas(self, nombre_delegacion):
        with open(RUTA_MUNICIPIOS, "r") as file:
            datos = json.load(file)
        for data in datos["features"]:
            if data["properties"]["NOMGEO"] == nombre_delegacion:
                return np.array(data["geometry"]["coordinates"][0])
        print(f"No se encontraron coordenadas para la delegación: {nombre_delegacion}")
        return None

    def get_measures(self, date_str, quadrant):
        year, day, date_obj = parse_date(date_str)
        h5_url = find_file(year, day, quadrant)
        if not h5_url:
            print("No se encontró el archivo.")
            return None
        save_path = f"/content/{date_obj}_{self.municipio}_{quadrant}.h5"
        h5_save_path = download_file(h5_url, save_path)
        if not h5_save_path:
            print("Fallo la descarga del archivo.")
            return None
        with h5py.File(h5_save_path, "r") as hdf_file:
            left_coord, right_coord = left_right_coords(hdf_file)
            image_matrix = hdf_file[IMAGE_PATH][()]
            coordenadas_municipio = self.extraer_coordenadas(self.municipio)
            copia_imagen = np.clip(image_matrix, 0, np.percentile(image_matrix, 99))
            fig, ax = plt.subplots(ncols=2, nrows = 3, figsize=(15, 15))
            ax[0][0].imshow(copia_imagen)
            ax[0][0].set_title(f"Imagen completa {self.municipio} - {date_obj}")
            imagen_recortada, nuevos_x, nuevos_y = recortar_imagen(image_matrix, coordenadas_municipio, left_coord, 1)
            copia_imagen = np.clip(imagen_recortada, 0, np.percentile(imagen_recortada, 99))
            ax[0][1].imshow(imagen_recortada)
            ax[0][1].set_title("Imagen recortada")
            # ... puedes seguir distribuyendo el resto de la lógica aquí ...
            plt.show()
            # Ejemplo de salida de datos
            datos = {
                "Fecha": date_obj,
                "Cantidad de pixeles": imagen_recortada.size,
                "Media de radianza": np.mean(imagen_recortada),
                "Desviación estándar de radianza": np.std(imagen_recortada),
                "Máximo de radianza": np.max(imagen_recortada),
                "Mínimo de radianza": np.min(imagen_recortada),
                "Percentil 25 de radianza": np.percentile(imagen_recortada, 25),
                "Percentil 50 de radianza": np.percentile(imagen_recortada, 50),
                "Percentil 75 de radianza": np.percentile(imagen_recortada, 75)
            }
            return pd.DataFrame(datos, index=[0]) 