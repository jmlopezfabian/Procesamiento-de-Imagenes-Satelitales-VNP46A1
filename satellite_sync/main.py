from processor import SatelliteProcessor

if __name__ == "__main__":
    processor = SatelliteProcessor("Iztapalapa")
    
    # Lista de fechas a procesar
    fechas = ["01-01-24", "02-01-24", "03-01-24"]
    
    # Procesar múltiples fechas y obtener dataframe con visualizaciones
    df = processor.run(fechas, "h08v07", show_plots=True)
    
    if not df.empty:
        print("Resultados obtenidos:")
        print(df)
    else:
        print("No se obtuvieron resultados.")