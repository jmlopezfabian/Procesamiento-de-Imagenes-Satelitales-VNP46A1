from processor import SatelliteProcessor

if __name__ == "__main__":
    processor = SatelliteProcessor("Iztapalapa")
    fecha = "01-01-24"
    df = processor.get_measures(fecha, "h08v07", show_plots=True)
    print(df)

