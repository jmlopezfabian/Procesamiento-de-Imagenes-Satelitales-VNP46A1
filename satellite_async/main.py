import nest_asyncio
from satellite_async import SatelliteImagesAsync
import asyncio
import pandas as pd
import time

# Configurar nest_asyncio para Jupyter/notebook
nest_asyncio.apply()

if __name__ == "__main__":
    municipios = ["azcapotzalco", "iztapalapa"]
    anio = 2024
    fechas_dt = pd.date_range(start=f"{anio}-01-01", end=f"{anio}-01-10", freq="D")
    fechas = fechas_dt.strftime("%d-%m-%y").tolist()
    
    sat = SatelliteImagesAsync(municipios)
    
    t1 = time.time()
    print("=== Ejemplo 1: Sin chunks (procesamiento original) ===")
    df1 = asyncio.run(sat.run(fechas))
    print(f"Resultados: {len(df1)} registros")
    t2 = time.time()
    print(f"Tiempo de ejecución: {t2 - t1} segundos")
    df1.to_parquet(f"../data/Iztapalapa_Tlalpan.parquet", index=False)
    print(f"\nResultados guardados en ../data/Iztapalapa_Tlalpan.parquet")
    print(df1.head())
    