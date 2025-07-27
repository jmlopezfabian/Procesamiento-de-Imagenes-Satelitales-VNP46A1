#!/usr/bin/env python3
"""
Ejemplo de uso del sistema modular de procesamiento satelital
"""

def ejemplo_basico():
    """Ejemplo básico de uso"""
    print("=== Ejemplo Básico ===")
    
    try:
        from processor import SatelliteProcessor
        
        # Crear procesador
        processor = SatelliteProcessor("Iztapalapa")
        print(f"Procesador creado para: {processor.municipio}")
        
        # Procesar una imagen (sin visualización para evitar problemas de Qt)
        resultado = processor.get_measures("01-01-24", "h08v06", show_plots=False)
        
        if resultado:
            print("✅ Procesamiento exitoso!")
            print(f"Fecha: {resultado.medicion.Fecha}")
            print(f"Píxeles procesados: {resultado.medicion.Cantidad_de_pixeles}")
            print(f"Media de radianza: {resultado.medicion.Media_de_radianza:.2f}")
            print(f"Desviación estándar: {resultado.medicion.Desviacion_estandar_de_radianza:.2f}")
            print(f"Máximo: {resultado.medicion.Maximo_de_radianza:.2f}")
            print(f"Mínimo: {resultado.medicion.Minimo_de_radianza:.2f}")
        else:
            print("❌ No se pudo procesar la imagen")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def ejemplo_multiple_fechas():
    """Ejemplo procesando múltiples fechas"""
    print("\n=== Ejemplo Múltiples Fechas ===")
    
    try:
        from processor import SatelliteProcessor
        import pandas as pd
        
        processor = SatelliteProcessor("Iztapalapa")
        fechas = ["01-01-24", "02-01-24", "03-01-24"]
        resultados = []
        
        for fecha in fechas:
            print(f"Procesando {fecha}...")
            resultado = processor.get_measures(fecha, "h08v06", show_plots=False)
            
            if resultado:
                resultados.append({
                    'Fecha': resultado.medicion.Fecha,
                    'Píxeles': resultado.medicion.Cantidad_de_pixeles,
                    'Media_Radianza': resultado.medicion.Media_de_radianza,
                    'Max_Radianza': resultado.medicion.Maximo_de_radianza,
                    'Min_Radianza': resultado.medicion.Minimo_de_radianza
                })
                print(f"  ✅ {fecha} procesado")
            else:
                print(f"  ❌ {fecha} falló")
        
        if resultados:
            df = pd.DataFrame(resultados)
            print("\nResumen de resultados:")
            print(df)
        else:
            print("No se procesaron fechas exitosamente")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def ejemplo_solo_recorte():
    """Ejemplo de solo recortar imagen"""
    print("\n=== Ejemplo Solo Recorte ===")
    
    try:
        from processor import SatelliteProcessor
        
        processor = SatelliteProcessor("Iztapalapa")
        
        # Solo recortar sin procesar completamente
        resultado = processor.recortar_imagen_solo("01-01-24", "h08v06")
        
        if resultado:
            imagen_recortada, copia_imagen, nuevos_x, nuevos_y = resultado
            print(f"✅ Imagen recortada: {imagen_recortada.shape}")
            print(f"Coordenadas X: {len(nuevos_x)} puntos")
            print(f"Coordenadas Y: {len(nuevos_y)} puntos")
        else:
            print("❌ No se pudo recortar la imagen")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Ejemplos de uso del sistema de procesamiento satelital\n")
    
    # Ejecutar ejemplos
    ejemplo_basico()
    ejemplo_multiple_fechas()
    ejemplo_solo_recorte()
    
    print("\n✨ Ejemplos completados!") 