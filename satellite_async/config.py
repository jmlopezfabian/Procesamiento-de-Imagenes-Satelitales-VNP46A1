import os

BASE_URL = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5000/VNP46A1/{year}/{day}/"
IMAGE_PATH = "HDFEOS/GRIDS/VNP_Grid_DNB/Data Fields/DNB_At_Sensor_Radiance_500m"
PIXELES_MUNICIPIOS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'municipios_coordenadas_pixeles.json')
TOKEN = os.getenv("NASA_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} 