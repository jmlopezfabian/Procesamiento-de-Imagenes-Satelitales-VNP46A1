import asyncio
import pandas as pd
import json
import os
from datetime import datetime
from satellite_async import SatelliteImagesAsync
from downloader import find_file, download_file
from processing import process_image
from models import MedicionResultado
from config import PIXELES_MUNICIPIOS, HEADERS
import aiohttp

class MultiMunicipioProcessor:
    """
    Procesa múltiples municipios de forma eficiente, descargando cada archivo H5 una sola vez
    """
    
    def __init__(self):
        self.municipios_data = self._load_municipios_data()
        self.cache_h5_files = {}  # Cache para archivos H5 ya descargados
        
    def _load_municipios_data(self):
        """Carga los datos de todos los municipios"""
        with open(PIXELES_MUNICIPIOS, 'r') as f:
            return json.load(f)
    
    def _get_municipios_by_cuadrante(self):
        """Agrupa municipios por cuadrante para optimizar descargas"""
        cuadrantes = {}
        for municipio, data in self.municipios_data.items():
            cuadrante = data['cuadrante']
            if cuadrante not in cuadrantes:
                cuadrantes[cuadrante] = []
            cuadrantes[cuadrante].append({
                'nombre': municipio,
                'coordenadas_pixeles': data['coordenadas_pixeles']
            })
        return cuadrantes
    
    async def _download_and_cache_h5(self, session, year, day, cuadrante, date_obj):
        """Descarga un archivo H5 y lo cachea para reutilización"""
        cache_key = f"{year}_{day}_{cuadrante}"
        
        if cache_key in self.cache_h5_files:
            print(f"✅ Usando archivo H5 cacheado: {cache_key}")
            return self.cache_h5_files[cache_key]
        
        # Buscar y descargar el archivo
        h5_url = await find_file(session, year, day, cuadrante)
        if not h5_url:
            return None
            
        save_path = f"../temp/{date_obj}_{cuadrante}.h5"
        downloaded_path = await download_file(session, h5_url, save_path)
        
        if downloaded_path:
            self.cache_h5_files[cache_key] = downloaded_path
            print(f"✅ Archivo H5 descargado y cacheado: {cache_key}")
            return downloaded_path
        
        return None
    
    async def _process_municipios_for_date(self, session, year, day, date_obj, municipios_in_cuadrante):
        """Procesa todos los municipios de un cuadrante para una fecha específica"""
        cuadrante = municipios_in_cuadrante[0]['cuadrante'] if municipios_in_cuadrante else None
        if not cuadrante:
            return []
        
        # Descargar archivo H5 una sola vez para todos los municipios
        h5_path = await self._download_and_cache_h5(session, year, day, cuadrante, date_obj)
        if not h5_path:
            return []
        
        results = []
        
        # Procesar cada municipio con el mismo archivo H5
        for municipio_data in municipios_in_cuadrante:
            try:
                datos = process_image(
                    h5_path, 
                    municipio_data['coordenadas_pixeles'], 
                    date_obj, 
                    municipio_data['nombre']
                )
                if datos:
                    results.append(datos.dict())
                    print(f"✅ Procesado: {municipio_data['nombre']} - {date_obj}")
            except Exception as e:
                print(f"❌ Error procesando {municipio_data['nombre']} para {date_obj}: {e}")
        
        return results
    
    async def process_all_municipios(self, fechas, chunks=None, save_progress=True):
        """Procesa todos los municipios para las fechas especificadas"""
        cuadrantes = self._get_municipios_by_cuadrante()
        all_results = []
        
        print(f"Procesando {len(self.municipios_data)} municipios en {len(cuadrantes)} cuadrantes")
        
        async with aiohttp.ClientSession() as session:
            for cuadrante, municipios in cuadrantes.items():
                print(f"\n=== Procesando cuadrante: {cuadrante} ({len(municipios)} municipios) ===")
                
                # Procesar fechas en chunks si se especifica
                if chunks:
                    fechas_chunks = [fechas[i:i + chunks] for i in range(0, len(fechas), chunks)]
                else:
                    fechas_chunks = [fechas]
                
                for chunk_idx, chunk_fechas in enumerate(fechas_chunks):
                    print(f"Procesando chunk {chunk_idx + 1}/{len(fechas_chunks)} con {len(chunk_fechas)} fechas")
                    
                    chunk_results = []
                    for fecha in chunk_fechas:
                        # Parsear fecha
                        date_obj = datetime.strptime(fecha, "%d-%m-%y").date()
                        year = date_obj.year
                        day = f"{date_obj.timetuple().tm_yday:03d}"
                        
                        # Procesar todos los municipios para esta fecha
                        date_results = await self._process_municipios_for_date(
                            session, year, day, date_obj, municipios
                        )
                        chunk_results.extend(date_results)
                    
                    all_results.extend(chunk_results)
                    
                    # Guardar progreso si está habilitado
                    if save_progress and chunk_results:
                        temp_df = pd.DataFrame(all_results)
                        self._save_progress(temp_df, f"multi_municipio_chunk_{chunk_idx + 1}")
        
        return pd.DataFrame(all_results)
    
    def _save_progress(self, df, chunk_name):
        """Guarda el progreso actual"""
        try:
            os.makedirs("../data", exist_ok=True)
            filename = f"../data/{chunk_name}.csv"
            df.to_csv(filename, index=False)
            print(f"✅ Progreso guardado: {filename} ({len(df)} registros)")
        except Exception as e:
            print(f"❌ Error guardando progreso: {e}")

# Función de conveniencia para usar fácilmente
async def process_all_municipios_async(fechas, chunks=None, save_progress=True):
    """Función de conveniencia para procesar todos los municipios"""
    processor = MultiMunicipioProcessor()
    return await processor.process_all_municipios(fechas, chunks, save_progress)