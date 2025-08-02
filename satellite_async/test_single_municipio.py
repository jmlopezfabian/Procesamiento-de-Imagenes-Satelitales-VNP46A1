import nest_asyncio
import asyncio
import pandas as pd
import os
from satellite_async import SatelliteImagesAsync

async def test_single_municipio():
    """Prueba con un solo municipio para comparar"""
    
    # Configurar nest_asyncio para Jupyter
    nest_asyncio.apply()
    
    # Solo 1 municipio
    municipio = "iztapalapa"
    
    # Solo 1 fecha
    fechas = ["01-01-24"]
    
    print(f"🧪 Test single: Procesando {municipio}")
    print(f"📅 Fecha: {fechas[0]}")
    
    try:
        # Crear instancia con un solo municipio
        sat = SatelliteImagesAsync(municipio)
        
        # Procesar sin chunks
        df = await sat.run(fechas, chunks=None, save_progress=False)
        
        if df is not None and not df.empty:
            print(f"✅ Test single exitoso!")
            print(f"📊 Total de registros: {len(df)}")
            print(f"🏙️ Municipios procesados: {df['Municipio'].nunique()}")
            
            # Mostrar todas las filas
            print("\n=== Todas las filas ===")
            print(df.to_string(index=False))
            
            return df
        else:
            print("⚠️ No se obtuvieron resultados en test single")
            return None
            
    except Exception as e:
        print(f"❌ Error durante test single: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Para ejecutar desde línea de comandos
    result = asyncio.run(test_single_municipio())
    if result is not None:
        print("\n✅ Test single completado!")
    else:
        print("\n❌ Test single falló!")

# Para usar en Jupyter/notebook:
# df = await test_single_municipio() 