import h5py
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Configurar backend no interactivo
#configuraar backend interactivo
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os
from typing import Optional, Tuple, List
from config import IMAGE_PATH, find_image_path
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
            
            # Encontrar la ruta correcta a los datos de imagen
            image_path = find_image_path(hdf_file)
            if image_path not in hdf_file:
                print(f"Error: No se encontró la ruta '{image_path}' en el archivo HDF5.")
                print("Estructura del archivo HDF5:")
                def print_structure(name, obj):
                    print(name)
                hdf_file.visititems(print_structure)
                return None
            
            image_matrix = hdf_file[image_path][()]
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

                # Preparar coordenadas de bordes incompletos para visualización (sin modificar la imagen)
                bordes_incompletos_x = []
                bordes_incompletos_y = []
                for i in range(len(nuevos_y)):
                    if (0 <= int(nuevos_y[i]) < imagen_recortada.shape[0] and 
                        0 <= int(nuevos_x[i]) < imagen_recortada.shape[1]):
                        bordes_incompletos_x.append(int(nuevos_x[i]))
                        bordes_incompletos_y.append(int(nuevos_y[i]))

                if show_plots:
                    ax[1][0].imshow(copia_imagen)
                    if bordes_incompletos_x:
                        ax[1][0].plot(bordes_incompletos_x, bordes_incompletos_y, 'k-', linewidth=1.5, alpha=0.8, label='Bordes')
                        ax[1][0].scatter(bordes_incompletos_x, bordes_incompletos_y, c='red', s=1, alpha=0.6)
                    ax[1][0].set_title("Imagen con bordes incompletos")

                # Completar bordes
                coordenadas_bordes = completar_bordes(nuevos_x, nuevos_y)

                # Preparar coordenadas de bordes completos para visualización (sin modificar la imagen)
                bordes_completos_x = []
                bordes_completos_y = []
                for coordenada in coordenadas_bordes:
                    if (0 <= coordenada[1] < imagen_recortada.shape[0] and 
                        0 <= coordenada[0] < imagen_recortada.shape[1]):
                        bordes_completos_x.append(coordenada[0])
                        bordes_completos_y.append(coordenada[1])

                if show_plots:
                    ax[1][1].imshow(copia_imagen)
                    if bordes_completos_x:
                        # Dibujar bordes como línea cerrada
                        if len(bordes_completos_x) > 1:
                            ax[1][1].plot(bordes_completos_x + [bordes_completos_x[0]], 
                                         bordes_completos_y + [bordes_completos_y[0]], 
                                         'k-', linewidth=2, alpha=0.9, label='Bordes completos')
                        ax[1][1].scatter(bordes_completos_x, bordes_completos_y, c='red', s=2, alpha=0.7)
                    ax[1][1].set_title("Imagen con bordes completos")

                
                # Calcular centroide y obtener píxeles principales
                cx, cy = polygon_centroid(coordenadas_bordes)
                coordenadas_pixeles_principales = get_pixeles(imagen_recortada, (cx, cy), coordenadas_bordes)
                
                # Detectar píxeles huérfanos (zonas no seleccionadas completamente rodeadas por bordes)
                coordenadas_pixeles_huerfanos = detect_orphan_pixels(imagen_recortada, coordenadas_bordes, coordenadas_pixeles_principales)

                # Extraer valores de píxeles principales (sin modificar la imagen)
                pixeles_principales = []
                pixeles_principales_coords = []
                for x, y in coordenadas_pixeles_principales:
                    if (0 <= y < imagen_recortada.shape[0] and 
                        0 <= x < imagen_recortada.shape[1]):
                        pixeles_principales.append(imagen_recortada[y, x])
                        pixeles_principales_coords.append((x, y))

                # Extraer valores de píxeles huérfanos (sin modificar la imagen)
                pixeles_huerfanos = []
                pixeles_huerfanos_coords = []
                for x, y in coordenadas_pixeles_huerfanos:
                    if (0 <= y < imagen_recortada.shape[0] and 
                        0 <= x < imagen_recortada.shape[1]):
                        pixeles_huerfanos.append(imagen_recortada[y, x])
                        pixeles_huerfanos_coords.append((x, y))

                # Combinar todos los píxeles para estadísticas generales
                pixeles_imagen = pixeles_principales + pixeles_huerfanos

                if show_plots:
                    ax[2][0].imshow(copia_imagen)
                    # Dibujar bordes
                    if bordes_completos_x:
                        if len(bordes_completos_x) > 1:
                            ax[2][0].plot(bordes_completos_x + [bordes_completos_x[0]], 
                                         bordes_completos_y + [bordes_completos_y[0]], 
                                         'k-', linewidth=2, alpha=0.9, label='Bordes')
                    # Dibujar píxeles principales como puntos
                    if pixeles_principales_coords:
                        px_coords = list(zip(*pixeles_principales_coords))
                        ax[2][0].scatter(px_coords[0], px_coords[1], c='blue', s=0.5, alpha=0.3, label='Píxeles principales')
                    # Dibujar píxeles huérfanos como puntos
                    if pixeles_huerfanos_coords:
                        hx_coords = list(zip(*pixeles_huerfanos_coords))
                        ax[2][0].scatter(hx_coords[0], hx_coords[1], c='red', s=0.5, alpha=0.3, label='Píxeles huérfanos')
                    ax[2][0].set_title("Imagen con pixeles seleccionados")
                    ax[2][0].legend(loc='upper right', fontsize=8)

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
            
            # Encontrar la ruta correcta a los datos de imagen
            image_path = find_image_path(hdf_file)
            if image_path not in hdf_file:
                print(f"Error: No se encontró la ruta '{image_path}' en el archivo HDF5.")
                print("Estructura del archivo HDF5:")
                def print_structure(name, obj):
                    print(name)
                hdf_file.visititems(print_structure)
                return None
                
            image_matrix = hdf_file[image_path][()]
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