from satellite_async import SatelliteImagesAsync
import asyncio

if __name__ == "__main__":
    municipio = "Iztapalapa"
    fechas = ["01-01-24", "02-01-24"]  # Ejemplo de fechas
    sat = SatelliteImagesAsync(municipio)
    df = asyncio.run(sat.run(fechas))
    print(df)