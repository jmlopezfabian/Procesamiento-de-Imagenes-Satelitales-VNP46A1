from satellite_sync import SatelliteProcessor


def main() -> None:
    municipio = "Iztapalapa"
    fechas = ["01-01-24"]
    tile = "h08v07"
    factor_escala = 1

    processor = SatelliteProcessor(municipio, factor_escala=factor_escala)
    df = processor.run(fechas, tile, show_plots=False, factor_escala=factor_escala)

    if df.empty:
        print("No se obtuvieron resultados.")
    else:
        print("Resultados obtenidos:")
        print(df.head())


if __name__ == "__main__":
    main()

