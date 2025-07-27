import requests
from bs4 import BeautifulSoup
import os
from config import BASE_URL, HEADERS, CHUNK_SIZE

def find_file(year: int, day: int, quadrant: str) -> str:
    """
    Busca el archivo .h5 correspondiente al año, día y cuadrante especificado.
    """
    url = BASE_URL.format(year=year, day=day)
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Error al acceder a {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a"):
        filename = link.get("href")
        if filename and quadrant in filename and filename.endswith(".h5"):
            return url + filename

    print(f"No se encontró archivo para {quadrant} en {year}-{day}")
    return None

def download_file(file_url: str, save_path: str) -> str:
    """
    Descarga un archivo desde una URL dada y lo guarda en la ruta especificada.
    """
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        response = requests.get(file_url, headers=HEADERS, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    file.write(chunk)
            
            # Verificar que el archivo descargado es válido
            if not is_valid_hdf5_file(save_path):
                print(f"El archivo descargado no es un archivo HDF5 válido: {save_path}")
                os.remove(save_path)  # Eliminar archivo inválido
                return None
                
            print(f"Archivo descargado: {save_path}")
            return save_path
        else:
            print(f"Error al descargar: {file_url} (Status: {response.status_code})")
            return None
            
    except Exception as e:
        print(f"Error durante la descarga: {e}")
        # Eliminar archivo parcial si existe
        if os.path.exists(save_path):
            os.remove(save_path)
        return None

def is_valid_hdf5_file(file_path: str) -> bool:
    """
    Verifica si un archivo es un archivo HDF5 válido.
    """
    try:
        # Verificar que el archivo existe y no está vacío
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return False
        
        # Leer los primeros bytes para verificar la firma HDF5
        with open(file_path, 'rb') as f:
            header = f.read(8)
            
        # La firma HDF5 comienza con estos bytes
        hdf5_signature = b'\x89HDF\r\n\x1a\n'
        
        if header == hdf5_signature:
            return True
        else:
            # Verificar si es HTML (página de error)
            with open(file_path, 'rb') as f:
                content_start = f.read(100)
                if b'<html' in content_start.lower() or b'<!doctype' in content_start.lower():
                    print("Se detectó contenido HTML (página de error)")
                    return False
                    
        return False
        
    except Exception as e:
        print(f"Error verificando archivo HDF5: {e}")
        return False 