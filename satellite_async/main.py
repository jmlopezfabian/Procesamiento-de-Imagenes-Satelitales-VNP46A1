from satellite_async import SatelliteImagesAsync
import asyncio
import pandas as pd
import time

if __name__ == "__main__":
    municipio = "Iztapalapa"
    anio = 2024
    fechas_dt = pd.date_range(start=f"{anio}-01-01", end=f"{anio}-01-10", freq="D")
    fechas = fechas_dt.strftime("%d-%m-%y").tolist()
    
    sat = SatelliteImagesAsync(municipio)
    
    t1 = time.time()
    print("=== Ejemplo 1: Sin chunks (procesamiento original) ===")
    df1 = asyncio.run(sat.run(fechas))
    print(f"Resultados: {len(df1)} registros")
    t2 = time.time()
    print(f"Tiempo de ejecución: {t2 - t1} segundos")
    print("\n=== Ejemplo 2: Con chunks de tamaño 2 ===")
    df2 = asyncio.run(sat.run(fechas, chunks=2))
    print(f"Resultados: {len(df2)} registros")
    t3 = time.time()
    print(f"Tiempo de ejecución: {t3 - t2} segundos")
    print("\n=== Ejemplo 3: Con chunks de tamaño 3 ===")
    df3 = asyncio.run(sat.run(fechas, chunks=5))
    print(f"Resultados: {len(df3)} registros")
    t4 = time.time()
    print(f"Tiempo de ejecución: {t4 - t3} segundos")
    # Guardar resultados
    df3.to_csv(f"../data/{municipio}.csv", index=False)
    print(f"\nResultados guardados en ../data/{municipio}.csv")