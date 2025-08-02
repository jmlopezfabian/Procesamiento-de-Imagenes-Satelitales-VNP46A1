import nest_asyncio
import asyncio
import pandas as pd
import os
import h5py
import numpy as np
from satellite_async import SatelliteImagesAsync
from utils import load_coord_data
from config import PIXELES_MUNICIPIOS, IMAGE_PATH

async def diagnostico_coordenadas():
    """Diagnostica las coordenadas de píxeles y el tamaño de la imagen"""
    
    # Configurar nest_asyncio para Jupyter
    nest_asyncio.apply()
    
    municipio = "coyoacan"
    fecha = "01-01-24"
    
    print(f"🔍 Diagnóstico para: {municipio} - {fecha}")
    
    try:
        # Cargar datos de coordenadas
        coord_data = load_coord_data(municipio, PIXELES_MUNICIPIOS)
        coordenadas_pixeles = coord_data.coordenadas_pixeles
        
        print(f"📊 Coordenadas cargadas para {municipio}:")
        print(f"  - Cuadrante: {coord_data.cuadrante}")
        print(f"  - Total de coordenadas: {len(coordenadas_pixeles)}")
        print(f"  - Primeras 5 coordenadas: {coordenadas_pixeles[:5]}")
        print(f"  - Últimas 5 coordenadas: {coordenadas_pixeles[-5:]}")
        
        # Calcular rangos de coordenadas
        x_coords = [coord[0] for coord in coordenadas_pixeles]
        y_coords = [coord[1] for coord in coordenadas_pixeles]
        
        print(f"📈 Rangos de coordenadas:")
        print(f"  - X: min={min(x_coords)}, max={max(x_coords)}")
        print(f"  - Y: min={min(y_coords)}, max={max(y_coords)}")
        
        # Crear instancia y descargar archivo
        sat = SatelliteImagesAsync(municipio)
        
        # Descargar archivo H5
        from datetime import datetime
        from utils import parse_date
        from downloader import find_file, download_file
        import aiohttp
        
        year, day, date_obj = parse_date(fecha)
        
        async with aiohttp.ClientSession() as session:
            # Buscar archivo
            h5_url = await find_file(session, year, day, coord_data.cuadrante)
            if not h5_url:
                print(f"❌ No se encontró archivo H5 para {year}-{day}")
                return None
            
            # Descargar archivo
            save_path = f"../temp/{date_obj}_{coord_data.cuadrante}.h5"
            downloaded_path = await download_file(session, h5_url, save_path)
            
            if not downloaded_path:
                print(f"❌ Error descargando archivo H5")
                return None
            
            print(f"✅ Archivo descargado: {downloaded_path}")
            
            # Analizar imagen
            with h5py.File(downloaded_path, "r") as hdf_file:
                image_matrix = hdf_file[IMAGE_PATH][()]
                
                print(f"📐 Dimensiones de la imagen:")
                print(f"  - Shape: {image_matrix.shape}")
                print(f"  - Filas: {image_matrix.shape[0]}")
                print(f"  - Columnas: {image_matrix.shape[1]}")
                
                # Verificar coordenadas válidas
                coordenadas_validas = []
                coordenadas_invalidas = []
                
                for x, y in coordenadas_pixeles:
                    if 0 <= y < image_matrix.shape[0] and 0 <= x < image_matrix.shape[1]:
                        coordenadas_validas.append((x, y))
                    else:
                        coordenadas_invalidas.append((x, y))
                
                print(f"✅ Coordenadas válidas: {len(coordenadas_validas)}")
                print(f"❌ Coordenadas inválidas: {len(coordenadas_invalidas)}")
                
                if coordenadas_invalidas:
                    print(f"⚠️ Ejemplos de coordenadas inválidas:")
                    for i, (x, y) in enumerate(coordenadas_invalidas[:5]):
                        print(f"  - ({x}, {y}) - X debe estar en [0, {image_matrix.shape[1]-1}], Y en [0, {image_matrix.shape[0]-1}]")
                
                # Procesar solo coordenadas válidas
                if coordenadas_validas:
                    pixeles_imagen = [image_matrix[y, x] for x, y in coordenadas_validas]
                    
                    print(f"📊 Estadísticas de píxeles válidos:")
                    print(f"  - Cantidad: {len(pixeles_imagen)}")
                    print(f"  - Media: {np.mean(pixeles_imagen):.2f}")
                    print(f"  - Min: {np.min(pixeles_imagen):.2f}")
                    print(f"  - Max: {np.max(pixeles_imagen):.2f}")
                    
                    # Crear resultado
                    from models import MedicionResultado
                    
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
                    
                    print(f"✅ Datos procesados exitosamente!")
                    print(f"  - Municipio: {datos.Municipio}")
                    print(f"  - Fecha: {datos.Fecha}")
                    print(f"  - Píxeles: {datos.Cantidad_de_pixeles}")
                    print(f"  - Media radianza: {datos.Media_de_radianza:.2f}")
                    
                    return datos.dict()
                else:
                    print(f"❌ No hay coordenadas válidas para procesar")
                    return None
            
    except Exception as e:
        print(f"❌ Error durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Para ejecutar desde línea de comandos
    result = asyncio.run(diagnostico_coordenadas())
    if result is not None:
        print("\n✅ Diagnóstico completado!")
    else:
        print("\n❌ Diagnóstico falló!")

# Para usar en Jupyter/notebook:
# df = await diagnostico_coordenadas() 