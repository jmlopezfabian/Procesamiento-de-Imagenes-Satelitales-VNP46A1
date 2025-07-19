import h5py
import numpy as np
import os
from .config import IMAGE_PATH
from .models import MedicionResultado

def process_image(downloaded_path, coordendas_pixeles, date_obj, municipio):
    if not os.path.exists(downloaded_path):
        print(f"Archivo no encontrado: {downloaded_path}")
        return None
    with open(downloaded_path, "rb") as f:
        start = f.read(15)
        if b"<html" in start or b"<!DOCTYPE html" in start:
            print(f"Archivo HTML recibido en vez de HDF5: {downloaded_path}")
            return None
    with h5py.File(downloaded_path, "r") as hdf_file:
        image_matrix = hdf_file[IMAGE_PATH][()]
        copia = np.clip(image_matrix.copy(), 0, np.percentile(image_matrix, 99))

        pixeles_imagen = [
            image_matrix[y, x]
            for x, y in coordendas_pixeles
            if 0 <= y < image_matrix.shape[0] and 0 <= x < image_matrix.shape[1]
        ]

        datos = MedicionResultado(
            Fecha=date_obj,
            Cantidad_de_pixeles=len(pixeles_imagen),
            Suma_de_radianza=float(np.sum(pixeles_imagen)),
            Media_de_radianza=float(np.mean(pixeles_imagen)),
            Desviacion_estandar_de_radianza=float(np.std(pixeles_imagen)),
            Maximo_de_radianza=float(np.max(pixeles_imagen)),
            Minimo_de_radianza=float(np.min(pixeles_imagen)),
            Percentil_25_de_radianza=float(np.percentile(pixeles_imagen, 25)),
            Percentil_50_de_radianza=float(np.percentile(pixeles_imagen, 50)),
            Percentil_75_de_radianza=float(np.percentile(pixeles_imagen, 75)),
        )

    os.remove(downloaded_path)
    return datos 