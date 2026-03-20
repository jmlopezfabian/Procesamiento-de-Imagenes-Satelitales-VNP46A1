import h5py
import math
import numpy as np
import os
from datetime import date
from typing import Any

from .config import IMAGE_PATH, find_image_path
from .models import MedicionResultado


def _float_to_json_safe(value: float) -> float | None:
    """Convert float to JSON-serializable value; NaN and Inf become None."""
    if math.isfinite(value):
        return float(value)
    return None


def extract_radiance_matrix(
    downloaded_path: str,
    coordenadas_pixeles: list[tuple[int, int]],
    date_obj: date,
    municipio: str,
) -> dict[str, Any] | None:
    """
    Extrae la submatriz de radianza y la máscara binaria del municipio, recortadas al bounding box.
    Devuelve dict con radiance_matrix, municipality_mask, bbox, rows, cols, municipio, fecha.
    """
    if not os.path.exists(downloaded_path):
        print(f"Archivo no encontrado: {downloaded_path}")
        return None

    try:
        with open(downloaded_path, "rb") as f:
            start = f.read(15)
            if b"<html" in start or b"<!DOCTYPE html" in start:
                print(f"Archivo HTML recibido en vez de HDF5: {downloaded_path}")
                return None

        with h5py.File(downloaded_path, "r") as hdf_file:
            radiance_path = find_image_path(hdf_file)
            image_matrix = hdf_file[radiance_path][()]

            # Filtrar coordenadas válidas dentro de la imagen
            coordenadas_validas = [
                (x, y)
                for x, y in coordenadas_pixeles
                if 0 <= y < image_matrix.shape[0] and 0 <= x < image_matrix.shape[1]
            ]

            if len(coordenadas_validas) == 0:
                print(
                    f"No se encontraron coordenadas válidas para {municipio} en {date_obj}"
                )
                return None

            # Bounding box
            min_x = min(x for x, _ in coordenadas_validas)
            max_x = max(x for x, _ in coordenadas_validas)
            min_y = min(y for _, y in coordenadas_validas)
            max_y = max(y for _, y in coordenadas_validas)

            # Submatriz de radianza recortada al bounding box
            submatrix = image_matrix[min_y : max_y + 1, min_x : max_x + 1]
            rows, cols = submatrix.shape

            # Máscara binaria: 1 = municipio, 0 = no municipio
            mask = np.zeros((rows, cols), dtype=int)
            for x, y in coordenadas_validas:
                mask[y - min_y, x - min_x] = 1

            # Convertir a listas anidadas con NaN/Inf -> None
            radiance_list: list[list[float | None]] = [
                [_float_to_json_safe(float(v)) for v in row] for row in submatrix
            ]
            mask_list: list[list[int]] = [list(row) for row in mask]

            return {
                "municipio": municipio,
                "fecha": date_obj,
                "bbox": {"min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y},
                "rows": rows,
                "cols": cols,
                "radiance_matrix": radiance_list,
                "municipality_mask": mask_list,
            }
    except Exception as e:
        print(f"Error extrayendo matriz de {downloaded_path}: {e}")
        return None


def process_image(downloaded_path, coordendas_pixeles, date_obj, municipio, delete_file=True):
    if not os.path.exists(downloaded_path):
        print(f"Archivo no encontrado: {downloaded_path}")
        return None
    
    try:
        with open(downloaded_path, "rb") as f:
            start = f.read(15)
            if b"<html" in start or b"<!DOCTYPE html" in start:
                print(f"Archivo HTML recibido en vez de HDF5: {downloaded_path}")
                return None
        
        with h5py.File(downloaded_path, "r") as hdf_file:
            radiance_path = find_image_path(hdf_file)
            image_matrix = hdf_file[radiance_path][()]
            copia = np.clip(image_matrix.copy(), 0, np.percentile(image_matrix, 99))

            # Filtrar coordenadas válidas
            coordenadas_validas = [
                (x, y) for x, y in coordendas_pixeles
                if 0 <= y < image_matrix.shape[0] and 0 <= x < image_matrix.shape[1]
            ]
            
            # Verificar que tenemos coordenadas válidas
            if len(coordenadas_validas) == 0:
                print(f"⚠️ No se encontraron coordenadas válidas para {municipio} en {date_obj}")
                print(f"   - Total coordenadas: {len(coordendas_pixeles)}")
                print(f"   - Dimensiones imagen: {image_matrix.shape}")
                print(f"   - Rango X: [0, {image_matrix.shape[1]-1}]")
                print(f"   - Rango Y: [0, {image_matrix.shape[0]-1}]")
                return None
            
            # Extraer píxeles válidos
            pixeles_imagen = [image_matrix[y, x] for x, y in coordenadas_validas]
            
            # Informar sobre coordenadas filtradas
            if len(coordenadas_validas) < len(coordendas_pixeles):
                print(f"ℹ️ Filtradas {len(coordendas_pixeles) - len(coordenadas_validas)} coordenadas inválidas para {municipio}")
                print(f"   - Coordenadas válidas: {len(coordenadas_validas)}")
                print(f"   - Coordenadas totales: {len(coordendas_pixeles)}")

            datos = MedicionResultado(
                Fecha=date_obj,
                Municipio=municipio,
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
        
        return datos
    
    except Exception as e:
        print(f"Error procesando archivo {downloaded_path}: {e}")
        return None
    
    finally:
        # Eliminar el archivo solo si delete_file=True
        if delete_file:
            try:
                if os.path.exists(downloaded_path):
                    os.remove(downloaded_path)
                    print(f"Archivo eliminado: {downloaded_path}")
            except Exception as e:
                print(f"Error eliminando archivo {downloaded_path}: {e}") 