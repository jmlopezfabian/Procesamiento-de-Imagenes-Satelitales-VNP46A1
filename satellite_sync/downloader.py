import requests
from bs4 import BeautifulSoup
from .config import BASE_URL, HEADERS

def find_file(year, day, quadrant):
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

def download_file(file_url, save_path):
    response = requests.get(file_url, headers=HEADERS, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Archivo descargado: {save_path}")
        return save_path
    else:
        print(f"Error al descargar: {file_url}")
        return None 