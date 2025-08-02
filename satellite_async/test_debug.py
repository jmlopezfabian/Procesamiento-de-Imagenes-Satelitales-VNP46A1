import nest_asyncio
import asyncio
import pandas as pd
import os
from satellite_async import SatelliteImagesAsync

async def test_debug():
    """Prueba de debug para múltiples municipios"""
    
    # Configurar nest_asyncio para Jupyter
    nest_asyncio.apply()
    
    # Solo 2 municipios para prueba
    municipios = ["iztapalapa", "coyoacan"]
    
    # Solo 1 fecha para debug
    fechas = ["01-01-24"]
    
    print(f"🧪 Debug: Procesando {len(municipios)} municipios")
    print(f"📅 Fecha: {fechas[0]}")
    
    try:
        # Crear instancia
        sat = SatelliteImagesAsync(municipios)
        
        # Procesar sin chunks para ver todo el proceso
        df = await sat.run(fechas, chunks=None, save_progress=False)
        
        if df is not None and not df.empty:
            print(f"✅ Debug exitoso!")
            print(f"📊 Total de registros: {len(df)}")
            print(f"🏙️ Municipios procesados: {df['Municipio'].nunique()}")
            
            # Mostrar todas las filas
            print("\n=== Todas las filas ===")
            print(df.to_string(index=False))
            
            return df
        else:
            print("⚠️ No se obtuvieron resultados en debug")
            return None
            
    except Exception as e:
        print(f"❌ Error durante debug: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Para ejecutar desde línea de comandos
    result = asyncio.run(test_debug())
    if result is not None:
        print("\n✅ Debug completado!")
    else:
        print("\n❌ Debug falló!")

# Para usar en Jupyter/notebook:
# df = await test_debug() 