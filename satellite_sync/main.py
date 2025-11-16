from processor import SatelliteProcessor


if __name__ == "__main__":
    # Configuración del procesador
    municipio = "Iztapalapa"
    factor_escala = 1  # Factor de escala modificable (1 = sin escalado, 2 = doble tamaño, etc.)
    
    processor = SatelliteProcessor(municipio, factor_escala=factor_escala)
    
    # Lista de fechas a procesar
    fechas = ["01-01-24"]
    
    # Procesar múltiples fechas y obtener dataframe con visualizaciones
    df = processor.run(fechas, "h08v07", show_plots=True, factor_escala=factor_escala)
    
    if not df.empty:
        print("Resultados obtenidos:")
        print(df)
    else:
        print("No se obtuvieron resultados.")
