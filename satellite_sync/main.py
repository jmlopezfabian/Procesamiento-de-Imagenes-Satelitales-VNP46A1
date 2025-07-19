from satellite_sync.satellite_sync import SatelliteImages

if __name__ == "__main__":
    municipio = "Iztapalapa"
    fechas = ["01-01-24", "02-01-24"]
    cuadrante = "h08v07"
    sat = SatelliteImages(municipio)
    for fecha in fechas:
        df = sat.get_measures(fecha, cuadrante)
        print(df) 