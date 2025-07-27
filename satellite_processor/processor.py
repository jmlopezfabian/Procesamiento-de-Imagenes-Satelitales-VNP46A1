import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import Optional, Tuple
from config import IMAGE_PATH
from models import MedicionResultado, ImagenProcesada, ResultadoProcesamiento
from utils import parse_date, extraer_coordenadas, left_right_coords, polygon_centroid
from downloader import find_file, download_file
from image_processor import recortar_imagen, completar_bordes, get_pixeles

class SatelliteProcessor:
    """
    Clase principal para procesar imágenes satelitales del producto VNP46A1.
    """
    
    def __init__(self, municipio: str):
        self.municipio = municipio
    
    def get_measures(self, date_str: str, quadrant: str, show_plots: bool = True) -> Optional[ResultadoProcesamiento]:
        """
        Consulta, descarga y extrae las coordenadas de una imagen satelital para un día y cuadrante.
        
        Args:
            date_str: Fecha en formato dd-mm-yy
            quadrant: Cuadrante de la imagen
            show_plots: Si mostrar las gráficas de visualización
            
        Returns:
            ResultadoProcesamiento con las mediciones y datos procesados
        """
        year, day, date_obj = parse_date(date_str)

        # Buscar y descargar archivo
        h5_url = find_file(year, day, quadrant)
        if not h5_url:
            print("No se encontró el archivo.")
            return None

        save_path = f"../temp/{date_obj}_{self.municipio}_{quadrant}.h5"
        h5_save_path = download_file(h5_url, save_path)
        if not h5_save_path:
            print("Fallo la descarga del archivo.")
            return None
        
        with h5py.File(h5_save_path, "r") as hdf_file:
            left_coord, right_coord = left_right_coords(hdf_file)
            if left_coord is None or right_coord is None:
                print("No se pudieron extraer las coordenadas del archivo HDF.")
                return None
            image_matrix = hdf_file[IMAGE_PATH][()]
            coordenadas_municipio = extraer_coordenadas(self.municipio)
            print(f"Debug: {coordenadas_municipio}")
            if coordenadas_municipio is None:
                print("No se pudieron extraer las coordenadas del municipio.")
                return None

            # Crear copia para visualización
            copia_imagen = np.clip(image_matrix, 0, np.percentile(image_matrix, 99))

            if show_plots:
                fig, ax = plt.subplots(ncols=2, nrows=3, figsize=(15, 15))
                ax[0][0].imshow(copia_imagen)
                ax[0][0].set_title(f"Imagen completa {self.municipio} - {date_obj}")
                
            # Recortar imagen
            try:
                imagen_recortada, nuevos_x, nuevos_y = recortar_imagen(
                    image_matrix, coordenadas_municipio, left_coord, 1
                )
                
                # Validar que la imagen recortada no esté vacía
                if imagen_recortada.size == 0:
                    print("La imagen recortada está vacía. Verifica las coordenadas del municipio.")
                    return None
                    
                copia_imagen = np.clip(imagen_recortada, 0, np.percentile(imagen_recortada, 99))

                if show_plots:
                    ax[0][1].imshow(imagen_recortada)
                    ax[0][1].set_title("Imagen recortada")

                # Marcar bordes incompletos
                for i in range(len(nuevos_y)):
                    if (0 <= int(nuevos_y[i]) < imagen_recortada.shape[0] and 
                        0 <= int(nuevos_x[i]) < imagen_recortada.shape[1]):
                        copia_imagen[int(nuevos_y[i]), int(nuevos_x[i])] = 2500

                if show_plots:
                    ax[1][0].imshow(copia_imagen)
                    ax[1][0].set_title("Imagen con bordes incompletos")

                # Completar bordes
                coordenadas_bordes = completar_bordes(nuevos_x, nuevos_y)

                for coordenada in coordenadas_bordes:
                    if (0 <= coordenada[1] < imagen_recortada.shape[0] and 
                        0 <= coordenada[0] < imagen_recortada.shape[1]):
                        copia_imagen[coordenada[1], coordenada[0]] = 2500

                if show_plots:
                    ax[1][1].imshow(copia_imagen)
                    ax[1][1].set_title("Imagen con bordes completos")

                print("Numero de bordes completos: ", len(coordenadas_bordes))
                
                # Calcular centroide y obtener píxeles
                cx, cy = polygon_centroid(coordenadas_bordes)
                coordenadas_pixeles_imagen = get_pixeles(imagen_recortada, (cx, cy), coordenadas_bordes)

                # Extraer valores de píxeles
                pixeles_imagen = []
                for x, y in coordenadas_pixeles_imagen:
                    if (0 <= y < imagen_recortada.shape[0] and 
                        0 <= x < imagen_recortada.shape[1]):
                        copia_imagen[y, x] = 2500
                        pixeles_imagen.append(imagen_recortada[y, x])

                if show_plots:
                    ax[2][0].imshow(copia_imagen)
                    ax[2][0].set_title("Imagen con pixeles seleccionados")

                    if pixeles_imagen:  # Solo mostrar histograma si hay píxeles
                        ax[2][1].hist(pixeles_imagen, bins=50)
                        ax[2][1].grid(True)
                        ax[2][1].set_title("Histograma de radiación")
                    else:
                        ax[2][1].text(0.5, 0.5, "No hay píxeles seleccionados", 
                                    ha='center', va='center', transform=ax[2][1].transAxes)
                        ax[2][1].set_title("Sin datos")

                # Validar que hay píxeles para procesar
                if not pixeles_imagen:
                    print("No se encontraron píxeles dentro del área del municipio.")
                    return None

                # Crear medición
                medicion = MedicionResultado(
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

                # Crear imagen procesada
                imagen_procesada = ImagenProcesada(
                    imagen_recortada=imagen_recortada,
                    imagen_visualizacion=copia_imagen,
                    coordenadas_x=nuevos_x,
                    coordenadas_y=nuevos_y
                )

                # Crear resultado completo
                resultado = ResultadoProcesamiento(
                    medicion=medicion,
                    imagen_procesada=imagen_procesada,
                    pixeles_seleccionados=pixeles_imagen
                )

                if show_plots:
                    plt.show()
                
                print(medicion)
                return resultado
                
            except Exception as e:
                print(f"Error durante el procesamiento de la imagen: {e}")
                return None

    def recortar_imagen_solo(self, date_str: str, quadrant: str) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
        """
        Solo recorta la imagen sin hacer mediciones completas.
        
        Args:
            date_str: Fecha en formato dd-mm-yy
            quadrant: Cuadrante de la imagen
            
        Returns:
            Tuple con (imagen_recortada, copia_imagen, nuevos_x, nuevos_y)
        """
        year, day, date_obj = parse_date(date_str)

        h5_url = find_file(year, day, quadrant)
        if not h5_url:
            print("No se encontró el archivo.")
            return None

        save_path = f"../temp/{date_obj}_{self.municipio}_{quadrant}.h5"
        h5_save_path = download_file(h5_url, save_path)
        if not h5_save_path:
            print("Fallo la descarga del archivo.")
            return None

        with h5py.File(h5_save_path, "r") as hdf_file:
            left_coord, right_coord = left_right_coords(hdf_file)
            if left_coord is None or right_coord is None:
                print("No se pudieron extraer las coordenadas del archivo HDF.")
                return None
                
            image_matrix = hdf_file[IMAGE_PATH][()]
            coordenadas_municipio = extraer_coordenadas(self.municipio)
            
            if coordenadas_municipio is None:
                print("No se pudieron extraer las coordenadas del municipio.")
                return None

            copia_imagen = np.clip(image_matrix, 0, np.percentile(image_matrix, 99))
            
            try:
                imagen_recortada, nuevos_x, nuevos_y = recortar_imagen(
                    image_matrix, coordenadas_municipio, left_coord, 1
                )
                
                if imagen_recortada.size == 0:
                    print("La imagen recortada está vacía. Verifica las coordenadas del municipio.")
                    return None
                    
                copia_imagen = np.clip(imagen_recortada, 0, np.percentile(imagen_recortada, 99))
                
                return imagen_recortada, copia_imagen, nuevos_x, nuevos_y
                
            except Exception as e:
                print(f"Error durante el recorte de la imagen: {e}")
                return None 