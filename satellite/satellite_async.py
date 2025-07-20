import asyncio
import pandas as pd
from config import PIXELES_MUNICIPIOS
from utils import normalize_municipio, parse_date, load_coord_data
from downloader import find_file, download_file
from processing import process_image
from models import MedicionResultado

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

    async def run(self, fechas):
        results = []
        import aiohttp
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_measures(session, f) for f in fechas]
            for result in asyncio.as_completed(tasks):
                datos = await result
                if datos:
                    results.append(datos.dict())
        return pd.DataFrame(results) 