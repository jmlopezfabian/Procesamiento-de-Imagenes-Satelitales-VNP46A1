import os

# URLs y rutas
BASE_URL = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5000/VNP46A1/{year}/{day}/"
IMAGE_PATH = "HDFEOS/GRIDS/VNP_Grid_DNB/Data Fields/DNB_At_Sensor_Radiance_500m"
RUTA_MUNICIPIOS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'limite-de-las-alcaldas.json')

# Token de autenticación
TOKEN = os.getenv("NASA_API_TOKEN")

# Headers para requests
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Configuración de procesamiento
CHUNK_SIZE = 8192
CONVERSION_FACTOR = 1_000_000 