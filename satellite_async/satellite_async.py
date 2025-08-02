import asyncio
import pandas as pd
import os
import glob
from config import PIXELES_MUNICIPIOS
from utils import normalize_municipio, parse_date, load_coord_data
from downloader import find_file, download_file
from processing import process_image
from models import MedicionResultado

def chunk_list(lst, chunk_size):
    """Divide una lista en chunks del tamaño especificado"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def cleanup_temp_files():
    """Limpia archivos .h5 residuales en el directorio temp"""
    temp_dir = "../temp"
    if os.path.exists(temp_dir):
        h5_files = glob.glob(os.path.join(temp_dir, "*.h5"))
        for file_path in h5_files:
            try:
                os.remove(file_path)
                print(f"Archivo residual eliminado: {file_path}")
            except Exception as e:
                print(f"Error eliminando archivo residual {file_path}: {e}")

def save_progress(df, municipio, chunk_number=None):
    """Guarda el progreso actual en un CSV"""
    try:
        # Crear directorio si no existe
        os.makedirs("../data", exist_ok=True)
        
        # Nombre del archivo con información del chunk
        if chunk_number is not None:
            filename = f"../data/{municipio}_progress_chunk_{chunk_number}.csv"
        else:
            filename = f"../data/{municipio}_progress.csv"
        
        # Guardar CSV
        df.to_csv(filename, index=False)
        print(f"✅ Progreso guardado: {filename} ({len(df)} registros)")
        return filename
    except Exception as e:
        print(f"❌ Error guardando progreso: {e}")
        return None

async def process_chunks(satellite_instance, fechas, chunks, session, municipio):
    """Procesa las fechas en chunks de forma asíncrona con guardado progresivo"""
    results = []
    fechas_chunks = chunk_list(fechas, chunks)
    
    for i, chunk_fechas in enumerate(fechas_chunks):
        print(f"Procesando chunk {i+1}/{len(fechas_chunks)} con {len(chunk_fechas)} fechas")
        
        try:
            # Procesar el chunk actual de forma asíncrona
            tasks = [satellite_instance.get_measures(session, f) for f in chunk_fechas]
            chunk_results = []
            
            for result in asyncio.as_completed(tasks):
                datos = await result
                if datos:
                    chunk_results.append(datos.dict())
            
            # Agregar resultados del chunk actual
            results.extend(chunk_results)
            print(f"Chunk {i+1} completado. Resultados obtenidos: {len(chunk_results)}")
            
            # Guardar progreso después de cada chunk
            if chunk_results:
                temp_df = pd.DataFrame(results)
                save_progress(temp_df, municipio, i+1)
            
        except Exception as e:
            print(f"❌ Error procesando chunk {i+1}: {e}")
            # Guardar progreso hasta el momento en caso de error
            if results:
                temp_df = pd.DataFrame(results)
                save_progress(temp_df, municipio, f"error_chunk_{i+1}")
            raise e
    
    return results

class SatelliteImagesAsync:
    """
    Class for get the measures of the satellite images for multiple municipalities
    """
    
    def __init__(self, municipios):
        """
        Inicializa con una lista de municipios
        
        Args:
            municipios: Lista de nombres de municipios o string único
        """
        if isinstance(municipios, str):
            municipios = [municipios]
        
        self.municipios = [normalize_municipio(m) for m in municipios]
        self.coord_data_dict = {}
        self.cache_h5_files = {}  # Cache para archivos H5 ya descargados
        
        # Cargar datos de coordenadas para todos los municipios
        for municipio in self.municipios:
            self.coord_data_dict[municipio] = load_coord_data(municipio, PIXELES_MUNICIPIOS)
        
        print(f"✅ Inicializado con {len(self.municipios)} municipios: {', '.join(self.municipios)}")

    async def _download_and_cache_h5(self, session, year, day, cuadrante, date_obj):
        """Descarga un archivo H5 y lo cachea para reutilización"""
        cache_key = f"{year}_{day}_{cuadrante}"
        
        if cache_key in self.cache_h5_files:
            print(f"✅ Usando archivo H5 cacheado: {cache_key}")
            return self.cache_h5_files[cache_key]
        
        # Buscar y descargar el archivo
        print(f"🔍 Buscando archivo H5 para: {year}-{day} ({cuadrante})")
        h5_url = await find_file(session, year, day, cuadrante)
        if not h5_url:
            print(f"❌ No se encontró archivo H5 para: {year}-{day} ({cuadrante})")
            return None
            
        save_path = f"../temp/{date_obj}_{cuadrante}.h5"
        print(f"📥 Descargando: {h5_url} -> {save_path}")
        downloaded_path = await download_file(session, h5_url, save_path)
        
        if downloaded_path:
            self.cache_h5_files[cache_key] = downloaded_path
            print(f"✅ Archivo H5 descargado y cacheado: {cache_key}")
            return downloaded_path
        else:
            print(f"❌ Error descargando archivo H5: {h5_url}")
        
        return None

    async def get_measures_for_date(self, session, date_str):
        """Obtiene medidas para todos los municipios en una fecha específica"""
        year, day, date_obj = parse_date(date_str)
        results = []
        
        # Agrupar municipios por cuadrante para optimizar descargas
        municipios_por_cuadrante = {}
        for municipio in self.municipios:
            coord_data = self.coord_data_dict[municipio]
            cuadrante = coord_data.cuadrante
            if cuadrante not in municipios_por_cuadrante:
                municipios_por_cuadrante[cuadrante] = []
            municipios_por_cuadrante[cuadrante].append({
                'nombre': municipio,
                'coordenadas_pixeles': coord_data.coordenadas_pixeles
            })
        
        # Procesar cada cuadrante
        for cuadrante, municipios_in_cuadrante in municipios_por_cuadrante.items():
            # Descargar archivo H5 una sola vez para todos los municipios del cuadrante
            h5_path = await self._download_and_cache_h5(session, year, day, cuadrante, date_obj)
            if not h5_path:
                continue
            
            # Procesar cada municipio con el mismo archivo H5
            for municipio_data in municipios_in_cuadrante:
                try:
                    datos = process_image(
                        h5_path, 
                        municipio_data['coordenadas_pixeles'], 
                        date_obj, 
                        municipio_data['nombre'],
                        delete_file=False  # No eliminar el archivo hasta procesar todos los municipios
                    )
                    if datos:
                        results.append(datos.dict())
                        print(f"✅ Procesado: {municipio_data['nombre']} - {date_obj}")
                    else:
                        print(f"⚠️ Sin datos para: {municipio_data['nombre']} - {date_obj}")
                except Exception as e:
                    print(f"❌ Error procesando {municipio_data['nombre']} para {date_obj}: {e}")
            
            # Eliminar el archivo H5 después de procesar todos los municipios del cuadrante
            try:
                if os.path.exists(h5_path):
                    os.remove(h5_path)
                    print(f"Archivo eliminado después de procesar todos los municipios: {h5_path}")
            except Exception as e:
                print(f"Error eliminando archivo {h5_path}: {e}")
        
        return results

    async def run(self, fechas, chunks=None, save_progress=True):
        results = []
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                if chunks is None:
                    # Procesamiento original: todas las fechas de forma asíncrona
                    tasks = [self.get_measures_for_date(session, f) for f in fechas]
                    for result in asyncio.as_completed(tasks):
                        datos_list = await result
                        if datos_list:
                            results.extend(datos_list)
                else:
                    # Procesamiento por chunks
                    fechas_chunks = chunk_list(fechas, chunks)
                    
                    for i, chunk_fechas in enumerate(fechas_chunks):
                        print(f"Procesando chunk {i+1}/{len(fechas_chunks)} con {len(chunk_fechas)} fechas")
                        
                        try:
                            # Procesar el chunk actual de forma asíncrona
                            tasks = [self.get_measures_for_date(session, f) for f in chunk_fechas]
                            chunk_results = []
                            
                            for result in asyncio.as_completed(tasks):
                                datos_list = await result
                                if datos_list:
                                    chunk_results.extend(datos_list)
                            
                            # Agregar resultados del chunk actual
                            results.extend(chunk_results)
                            print(f"Chunk {i+1} completado. Resultados obtenidos: {len(chunk_results)}")
                            
                            # Guardar progreso después de cada chunk
                            if chunk_results and save_progress:
                                temp_df = pd.DataFrame(results)
                                save_progress(temp_df, f"multi_municipio_chunk_{i+1}")
                            
                        except Exception as e:
                            print(f"❌ Error procesando chunk {i+1}: {e}")
                            # Guardar progreso hasta el momento en caso de error
                            if results and save_progress:
                                temp_df = pd.DataFrame(results)
                                save_progress(temp_df, f"error_chunk_{i+1}")
                            raise e
        except Exception as e:
            print(f"❌ Error durante el procesamiento: {e}")
            # Guardar progreso hasta el momento en caso de error
            if results and save_progress:
                temp_df = pd.DataFrame(results)
                save_progress(temp_df, "error_final")
            raise e
        finally:
            # Limpiar archivos residuales al final
            cleanup_temp_files()
        
        return pd.DataFrame(results)