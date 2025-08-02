import nest_asyncio
import asyncio
import aiohttp
from downloader import find_file, download_file
from utils import parse_date

async def debug_url_problem():
    """Debuggea el problema de la URL de descarga"""
    
    nest_asyncio.apply()
    
    # Parámetros de prueba
    fecha = "01-01-24"
    cuadrante = "h08v07"
    
    year, day, date_obj = parse_date(fecha)
    
    print(f"🔍 Debuggeando URL para: {year}-{day} ({cuadrante})")
    
    async with aiohttp.ClientSession() as session:
        # Paso 1: Buscar archivo
        print(f"📥 Buscando archivo H5...")
        h5_url = await find_file(session, year, day, cuadrante)
        
        if not h5_url:
            print(f"❌ No se encontró URL")
            return
        
        print(f"✅ URL encontrada: {h5_url}")
        
        # Paso 2: Verificar contenido de la URL
        print(f"🔍 Verificando contenido de la URL...")
        try:
            async with session.get(h5_url) as response:
                print(f"📊 Status: {response.status}")
                print(f"📊 Headers: {dict(response.headers)}")
                
                # Leer los primeros bytes para verificar el tipo de contenido
                content = await response.read()
                print(f"📊 Tamaño del contenido: {len(content)} bytes")
                print(f"📊 Primeros 100 bytes: {content[:100]}")
                
                # Verificar si es HTML
                if b"<html" in content[:1000] or b"<!DOCTYPE" in content[:1000]:
                    print(f"❌ El contenido es HTML, no HDF5")
                    print(f"📄 Contenido HTML:")
                    print(content[:500].decode('utf-8', errors='ignore'))
                else:
                    print(f"✅ El contenido parece ser HDF5")
                    
        except Exception as e:
            print(f"❌ Error verificando URL: {e}")
        
        # Paso 3: Intentar descarga normal
        print(f"\n📥 Intentando descarga normal...")
        save_path = f"../temp/debug_{date_obj}_{cuadrante}.h5"
        downloaded_path = await download_file(session, h5_url, save_path)
        
        if downloaded_path:
            print(f"✅ Archivo descargado: {downloaded_path}")
            
            # Verificar tamaño
            import os
            size = os.path.getsize(downloaded_path)
            print(f"📊 Tamaño del archivo: {size} bytes")
            
            # Verificar contenido
            with open(downloaded_path, 'rb') as f:
                start = f.read(1000)
                if b"<html" in start or b"<!DOCTYPE" in start:
                    print(f"❌ Archivo descargado es HTML")
                    print(f"📄 Contenido:")
                    print(start.decode('utf-8', errors='ignore'))
                else:
                    print(f"✅ Archivo descargado parece ser HDF5 válido")
            
            # Limpiar
            os.remove(downloaded_path)
        else:
            print(f"❌ Error en la descarga")

if __name__ == "__main__":
    asyncio.run(debug_url_problem())

# Para usar en Jupyter/notebook:
# await debug_url_problem() 