import h5py
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Configurar backend no interactivo
import matplotlib.pyplot as plt
import os
from typing import Optional, Tuple, List
from config import IMAGE_PATH
from models import MedicionResultado
from utils import parse_date, extraer_coordenadas, left_right_coords, polygon_centroid
from downloader import find_file, download_file
from image_processor import recortar_imagen, completar_bordes, get_pixeles, detect_orphan_pixels

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

class SatelliteProcessor:
    """
    Clase principal para procesar imágenes satelitales del producto VNP46A1.
    """
    
    def __init__(self, municipio: str, factor_escala: int = 1):
        self.municipio = municipio
        self.factor_escala = factor_escala
    
    def _save_plot(self, fig, date_obj: str, quadrant: str, plot_type: str = "analysis"):
        """
        Guarda una figura de matplotlib en lugar de mostrarla.
        
        Args:
            fig: Figura de matplotlib
            date_obj: Fecha del análisis
            quadrant: Cuadrante de la imagen
            plot_type: Tipo de gráfica
        """
        try:
            # Crear directorio temp si no existe
            os.makedirs("../temp", exist_ok=True)
            filename = f"../temp/{date_obj}_{self.municipio}_{quadrant}_{plot_type}.png"
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Gráfica guardada como: {filename}")
        except Exception as e:
            print(f"Error al guardar la gráfica: {e}")
        finally:
            plt.close(fig)
    
    def get_measures(self, date_str: str, quadrant: str, show_plots: bool = True, factor_escala: int = None) -> Optional[dict]:
        """
        Consulta, descarga y extrae las coordenadas de una imagen satelital para un día y cuadrante.
        
        Args:
            date_str: Fecha en formato dd-mm-yy
            quadrant: Cuadrante de la imagen
            show_plots: Si mostrar las gráficas de visualización
            factor_escala: Factor de escala para aumentar la resolución de la imagen (por defecto usa el del constructor)
            
        Returns:
            Diccionario con las mediciones o None si hay error
        """
        year, day, date_obj = parse_date(date_str)
        
        # Usar el factor de escala pasado como parámetro o el del constructor
        escala_a_usar = factor_escala if factor_escala is not None else self.factor_escala

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
                    image_matrix, coordenadas_municipio, left_coord, escala_a_usar
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

                
                # Calcular centroide y obtener píxeles principales
                cx, cy = polygon_centroid(coordenadas_bordes)
                coordenadas_pixeles_principales = get_pixeles(imagen_recortada, (cx, cy), coordenadas_bordes)
                
                # Detectar píxeles huérfanos (zonas no seleccionadas completamente rodeadas por bordes)
                coordenadas_pixeles_huerfanos = detect_orphan_pixels(imagen_recortada, coordenadas_bordes, coordenadas_pixeles_principales)

                # Extraer valores de píxeles principales
                pixeles_principales = []
                for x, y in coordenadas_pixeles_principales:
                    if (0 <= y < imagen_recortada.shape[0] and 
                        0 <= x < imagen_recortada.shape[1]):
                        copia_imagen[y, x] = 2500
                        pixeles_principales.append(imagen_recortada[y, x])

                # Extraer valores de píxeles huérfanos
                pixeles_huerfanos = []
                for x, y in coordenadas_pixeles_huerfanos:
                    if (0 <= y < imagen_recortada.shape[0] and 
                        0 <= x < imagen_recortada.shape[1]):
                        copia_imagen[y, x] = 3000  # Different color for orphan pixels
                        pixeles_huerfanos.append(imagen_recortada[y, x])

                # Combinar todos los píxeles para estadísticas generales
                pixeles_imagen = pixeles_principales + pixeles_huerfanos

                if show_plots:
                    ax[2][0].imshow(copia_imagen)
                    ax[2][0].set_title("Imagen con pixeles seleccionados")

                    if pixeles_imagen:  # Solo mostrar histograma si hay píxeles
                        ax[2][1].hist(pixeles_principales, bins=50, alpha=0.7, label='Main pixels', color='blue')
                        if pixeles_huerfanos:
                            ax[2][1].hist(pixeles_huerfanos, bins=50, alpha=0.7, label='Orphan pixels', color='red')
                        ax[2][1].grid(True)
                        ax[2][1].set_title("Histograma de radiación")
                        ax[2][1].legend()
                    else:
                        ax[2][1].text(0.5, 0.5, "No hay píxeles seleccionados", 
                                    ha='center', va='center', transform=ax[2][1].transAxes)
                        ax[2][1].set_title("Sin datos")

                # Validar que hay píxeles para procesar
                if not pixeles_imagen:
                    print("No se encontraron píxeles dentro del área del municipio.")
                    return None

                # Crear medición usando solo MedicionResultado
                medicion = MedicionResultado(
                    Fecha=date_obj,
                    Cantidad_de_pixeles=len(pixeles_imagen),
                    Cantidad_de_pixeles_principales=len(pixeles_principales),
                    Suma_de_radianza=float(np.sum(pixeles_imagen)),
                    Media_de_radianza=float(np.mean(pixeles_imagen)),
                    Desviacion_estandar_de_radianza=float(np.std(pixeles_imagen)),
                    Maximo_de_radianza=float(np.max(pixeles_imagen)),
                    Minimo_de_radianza=float(np.min(pixeles_imagen)),
                    Percentil_25_de_radianza=float(np.percentile(pixeles_imagen, 25)),
                    Percentil_50_de_radianza=float(np.percentile(pixeles_imagen, 50)),
                    Percentil_75_de_radianza=float(np.percentile(pixeles_imagen, 75)),
                )
                if show_plots:
                    # Guardar la figura usando la función 
                    plt.show()
                    self._save_plot(plt.gcf(), date_obj, quadrant, "analysis")
                os.remove(h5_save_path)
                return medicion.dict()
                
            except Exception as e:
                print(f"Error durante el procesamiento de la imagen: {e}")
                return None

    def run(self, fechas: List[str], quadrant: str = "h08v07", show_plots: bool = False, factor_escala: int = None) -> pd.DataFrame:
        """
        Procesa múltiples fechas y retorna un dataframe con los resultados.
        
        Args:
            fechas: Lista de fechas en formato dd-mm-yy
            quadrant: Cuadrante de la imagen (por defecto h08v07)
            show_plots: Si mostrar las visualizaciones de matplotlib
            factor_escala: Factor de escala para aumentar la resolución de la imagen (por defecto usa el del constructor)
            
        Returns:
            DataFrame con las mediciones de todas las fechas
        """
        results = []
        
        # Usar el factor de escala pasado como parámetro o el del constructor
        escala_a_usar = factor_escala if factor_escala is not None else self.factor_escala
        
        for fecha in fechas:
            print(f"Procesando fecha: {fecha}")
            try:
                datos = self.get_measures(fecha, quadrant, show_plots=show_plots, factor_escala=escala_a_usar)
                if datos:
                    results.append(datos)
                else:
                    print(f"No se pudieron obtener datos para {fecha}")
            except Exception as e:
                print(f"Error procesando {fecha}: {e}")
        
        if not results:
            print("No se obtuvieron datos para ninguna fecha.")
            return pd.DataFrame()
            
        return pd.DataFrame(results)

    def recortar_imagen_solo(self, date_str: str, quadrant: str, factor_escala: int = None) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
        """
        Solo recorta la imagen sin hacer mediciones completas.
        
        Args:
            date_str: Fecha en formato dd-mm-yy
            quadrant: Cuadrante de la imagen
            factor_escala: Factor de escala para aumentar la resolución de la imagen (por defecto usa el del constructor)
            
        Returns:
            Tuple con (imagen_recortada, copia_imagen, nuevos_x, nuevos_y)
        """
        year, day, date_obj = parse_date(date_str)
        
        # Usar el factor de escala pasado como parámetro o el del constructor
        escala_a_usar = factor_escala if factor_escala is not None else self.factor_escala

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
                    image_matrix, coordenadas_municipio, left_coord, escala_a_usar
                )
                
                if imagen_recortada.size == 0:
                    print("La imagen recortada está vacía. Verifica las coordenadas del municipio.")
                    return None
                    
                copia_imagen = np.clip(imagen_recortada, 0, np.percentile(imagen_recortada, 99))
                
                return imagen_recortada, copia_imagen, nuevos_x, nuevos_y
                
            except Exception as e:
                print(f"Error durante el recorte de la imagen: {e}")
                return None