import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from config import BASE_URL, HEADERS

async def find_file(session, year, day, cuadrante):
    url = BASE_URL.format(year=year, day=day)
    async with session.get(url, headers=HEADERS) as resp:
        if resp.status != 200:
            print(f"Error al acceder a {url}")
            return None
        text = await resp.text()
        soup = BeautifulSoup(text, "html.parser")
        for link in soup.find_all("a"):
            filename = link.get("href")
            if filename and cuadrante in filename and filename.endswith(".h5"):
                # Limpiar el href de espacios y saltos de línea
                filename = filename.strip()
                
                # Verificar si el href ya es una URL completa
                if filename.startswith("http"):
                    # Reemplazar saltos de línea y espacios extra
                    filename = filename.replace('\n', '').replace('\r', '').strip()
                    return filename
                else:
                    # Si es solo el nombre del archivo, concatenar con la URL base
                    full_url = url + filename
                    return full_url
    print(f"No se encontró archivo para cuadrante {cuadrante} en {url}")
    return None

async def download_file(session, url, path, max_retries=3, delay=2):
    """
    Descarga un archivo con sistema de retry
    
    Args:
        session: Sesión de aiohttp
        url: URL del archivo a descargar
        path: Ruta donde guardar el archivo
        max_retries: Número máximo de intentos (default: 3)
        delay: Delay entre intentos en segundos (default: 2)
    """
    for attempt in range(max_retries):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Configurar timeout más largo para archivos grandes
            timeout = aiohttp.ClientTimeout(total=300, connect=60)
            
            async with session.get(url, headers=HEADERS, timeout=timeout) as resp:
                if resp.status == 200:
                    print(f"Descargando: {url} (intento {attempt + 1}/{max_retries})")
                    total_size = 0
                    with open(path, "wb") as f:
                        while True:
                            chunk = await resp.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                            total_size += len(chunk)
                    
                    print(f"Descarga completada: {path} ({total_size} bytes)")
                    return path
                else:
                    print(f"Fallo la descarga del archivo: {url} - Status: {resp.status} (intento {attempt + 1}/{max_retries})")
                    # Intentar leer el cuerpo de la respuesta para más información
                    try:
                        error_text = await resp.text()
                        print(f"Respuesta del servidor: {error_text[:200]}")
                    except:
                        pass
                    
                    if attempt < max_retries - 1:
                        print(f"Reintentando en {delay} segundos...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        return None
                        
        except aiohttp.ClientError as e:
            print(f"Error de cliente HTTP al descargar {url}: {e} (intento {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                print(f"Reintentando en {delay} segundos...")
                await asyncio.sleep(delay)
                continue
            else:
                return None
        except asyncio.TimeoutError as e:
            print(f"Timeout al descargar {url}: {e} (intento {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                print(f"Reintentando en {delay} segundos...")
                await asyncio.sleep(delay)
                continue
            else:
                return None
        except RuntimeError as e:
            print(f"Error de runtime al descargar {url}: {e} (intento {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                print(f"Reintentando en {delay} segundos...")
                await asyncio.sleep(delay)
                continue
            else:
                return None
        except Exception as e:
            print(f"Error inesperado al descargar {url}: {e} (intento {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                print(f"Reintentando en {delay} segundos...")
                await asyncio.sleep(delay)
                continue
            else:
                return None
    
    return None