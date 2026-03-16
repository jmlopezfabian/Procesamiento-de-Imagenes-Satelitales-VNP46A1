import os
from dotenv import load_dotenv
from importlib import resources

load_dotenv()

BASE_URL = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5200/VNP46A1/{year}/{day}/"
IMAGE_PATH = "HDFEOS/GRIDS/VNP_Grid_DNB/Data Fields/DNB_At_Sensor_Radiance_500m"
_DATA_ROOT = resources.files("vnp46a1_data")
PIXELES_MUNICIPIOS = str(_DATA_ROOT.joinpath("municipios_coordenadas_pixeles.json"))
TOKEN = os.getenv("NASA_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}