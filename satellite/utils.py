import json
from datetime import datetime
from models import CoordenadasPixeles

def normalize_municipio(municipio: str) -> str:
    return municipio.lower().replace("á", "a").replace("é", "e")\
        .replace("í", "i").replace("ó", "o").replace("ú", "u")

def parse_date(date_str: str):
    date = datetime.strptime(date_str, "%d-%m-%y")
    return date.year, date.timetuple().tm_yday, date.date()

def load_coord_data(municipio: str, path: str) -> CoordenadasPixeles:
    with open(path, "r") as f:
        data = json.load(f)
    return CoordenadasPixeles(**data[municipio]) 