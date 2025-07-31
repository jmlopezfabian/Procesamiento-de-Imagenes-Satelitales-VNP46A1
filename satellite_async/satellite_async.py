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

async def process_chunks(satellite_instance, fechas, chunks, session):
    """Procesa las fechas en chunks de forma asíncrona"""
    results = []
    fechas_chunks = chunk_list(fechas, chunks)
    
    for i, chunk_fechas in enumerate(fechas_chunks):
        print(f"Procesando chunk {i+1}/{len(fechas_chunks)} con {len(chunk_fechas)} fechas")
        
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
    
    return results

class SatelliteImagesAsync:
    """
    Class for get the measures of the satellite images
    """
    
    def __init__(self, municipio):
        self.municipio = normalize_municipio(municipio)
        self.coord_data = load_coord_data(self.municipio, PIXELES_MUNICIPIOS)

    async def get_measures(self, session, date_str):
        cuadrante = self.coord_data.cuadrante
        coordendas_pixeles = self.coord_data.coordenadas_pixeles
        year, day, date_obj = parse_date(date_str)
        h5_url = await find_file(session, year, day, cuadrante)

        if not h5_url:
            return None

        save_path = f"../temp/{date_obj}_{self.municipio}_{cuadrante}.h5"
        downloaded_path = await download_file(session, h5_url, save_path)

        if not downloaded_path:
            return None

        datos = process_image(downloaded_path, coordendas_pixeles, date_obj, self.municipio)
        return datos

    async def run(self, fechas, chunks=None):
        results = []
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                if chunks is None:
                    # Procesamiento original: todas las fechas de forma asíncrona
                    tasks = [self.get_measures(session, f) for f in fechas]
                    for result in asyncio.as_completed(tasks):
                        datos = await result
                        if datos:
                            results.append(datos.dict())
                else:
                    # Procesamiento por chunks usando la función separada
                    results = await process_chunks(self, fechas, chunks, session)
        finally:
            # Limpiar archivos residuales al final
            cleanup_temp_files()
        
        return pd.DataFrame(results)