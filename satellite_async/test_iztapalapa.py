import nest_asyncio
import asyncio
from satellite_async import SatelliteImagesAsync

async def test_iztapalapa():
    """Prueba específicamente iztapalapa"""
    
    nest_asyncio.apply()
    
    print("🔍 Probando específicamente iztapalapa...")
    
    # Solo iztapalapa
    municipio = "iztapalapa"
    fechas = ["01-01-24"]
    
    sat = SatelliteImagesAsync(municipio)
    df = await sat.run(fechas, chunks=None, save_progress=False)
    
    if df is not None and not df.empty:
        print(f"✅ iztapalapa: EXITOSO")
        print(f"   - Registros: {len(df)}")
        print(f"   - Píxeles: {df['Cantidad_de_pixeles'].iloc[0]}")
        print(f"   - Media radianza: {df['Media_de_radianza'].iloc[0]:.2f}")
        print(f"   - Datos: {df.head()}")
    else:
        print(f"❌ iztapalapa: FALLÓ")

if __name__ == "__main__":
    asyncio.run(test_iztapalapa())

# Para usar en Jupyter/notebook:
# await test_iztapalapa() 