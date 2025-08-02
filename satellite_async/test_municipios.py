import nest_asyncio
import asyncio
import pandas as pd
import os
from satellite_async import SatelliteImagesAsync

async def test_municipios():
    """Prueba diferentes municipios para ver cuáles funcionan"""
    
    # Configurar nest_asyncio para Jupyter
    nest_asyncio.apply()
    
    # Lista de municipios para probar
    municipios_prueba = [
        "iztapalapa",
        "coyoacan", 
        "gustavo a. madero",
        "benito juarez",
        "azcapotzalco",
        "cuajimalpa de morelos"
    ]
    
    # Solo 1 fecha para prueba
    fechas = ["01-01-24"]
    
    print(f"🧪 Probando {len(municipios_prueba)} municipios...")
    
    resultados = {}
    
    for municipio in municipios_prueba:
        print(f"\n{'='*50}")
        print(f"🔍 Probando: {municipio}")
        print(f"{'='*50}")
        
        try:
            # Crear instancia con un solo municipio
            sat = SatelliteImagesAsync(municipio)
            
            # Procesar sin chunks
            df = await sat.run(fechas, chunks=None, save_progress=False)
            
            if df is not None and not df.empty:
                print(f"✅ {municipio}: EXITOSO")
                print(f"   - Registros: {len(df)}")
                print(f"   - Píxeles: {df['Cantidad_de_pixeles'].iloc[0]}")
                print(f"   - Media radianza: {df['Media_de_radianza'].iloc[0]:.2f}")
                resultados[municipio] = "EXITOSO"
            else:
                print(f"❌ {municipio}: FALLÓ")
                resultados[municipio] = "FALLÓ"
                
        except Exception as e:
            print(f"❌ {municipio}: ERROR - {e}")
            resultados[municipio] = f"ERROR: {str(e)}"
    
    # Resumen final
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN DE PRUEBAS")
    print(f"{'='*60}")
    
    exitosos = 0
    fallidos = 0
    
    for municipio, resultado in resultados.items():
        if "EXITOSO" in resultado:
            print(f"✅ {municipio}: {resultado}")
            exitosos += 1
        else:
            print(f"❌ {municipio}: {resultado}")
            fallidos += 1
    
    print(f"\n📈 Estadísticas:")
    print(f"   - Exitosos: {exitosos}")
    print(f"   - Fallidos: {fallidos}")
    print(f"   - Total: {len(resultados)}")
    
    return resultados

if __name__ == "__main__":
    # Para ejecutar desde línea de comandos
    result = asyncio.run(test_municipios())
    if result:
        print("\n✅ Pruebas completadas!")
    else:
        print("\n❌ Pruebas fallaron!")

# Para usar en Jupyter/notebook:
# resultados = await test_municipios() 