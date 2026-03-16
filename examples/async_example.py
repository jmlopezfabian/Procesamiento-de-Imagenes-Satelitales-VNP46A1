import asyncio
import pandas as pd

from satellite_async.satellite_async import SatelliteImagesAsync


async def main() -> None:
    municipios = ["azcapotzalco", "iztapalapa"]
    anio = 2024
    fechas_dt = pd.date_range(start=f"{anio}-01-01", end=f"{anio}-01-03", freq="D")
    fechas = fechas_dt.strftime("%d-%m-%y").tolist()

    sat = SatelliteImagesAsync(municipios)

    df = await sat.run(fechas)
    print(f"Resultados: {len(df)} registros")
    if not df.empty:
        print(df.head())


if __name__ == "__main__":
    asyncio.run(main())

