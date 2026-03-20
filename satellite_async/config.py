import os
from dotenv import load_dotenv
from importlib import resources

load_dotenv()

BASE_URL = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5200/VNP46A1/{year}/{day}/"
IMAGE_PATH = "HDFEOS/GRIDS/VNP_Grid_DNB/Data Fields/DNB_At_Sensor_Radiance_500m"


def find_image_path(hdf_file) -> str:
    """
    Encuentra la ruta al dataset de radianza. Colección 5200 puede usar
    VIIRS_Grid_DNB_2d o VNP_Grid_DNB; busca alternativas si el path estándar falla.
    """
    candidates = [
        IMAGE_PATH,
        "HDFEOS/GRIDS/VIIRS_Grid_DNB_2d/Data Fields/DNB_At_Sensor_Radiance_500m",
        "HDFEOS/GRIDS/VIIRS_Grid_DNB_2d/Data Fields/DNB_At_Sensor_Radiance",
    ]
    for path in candidates:
        try:
            if path in hdf_file:
                return path
        except Exception:
            pass

    try:
        if "HDFEOS" in hdf_file and "GRIDS" in hdf_file["HDFEOS"]:
            grids = hdf_file["HDFEOS"]["GRIDS"]
            for grid_name in list(grids.keys()):
                grid = grids[grid_name]
                for key in list(grid.keys()):
                    if "Data" in key and "Field" in key:
                        data_fields = grid[key]
                        for field_name in list(data_fields.keys()):
                            if "Radiance" in field_name and "DNB" in field_name:
                                path = f"HDFEOS/GRIDS/{grid_name}/{key}/{field_name}"
                                try:
                                    if path in hdf_file:
                                        return path
                                except Exception:
                                    pass
    except Exception:
        pass

    return IMAGE_PATH
_DATA_ROOT = resources.files("vnp46a1_data")
PIXELES_MUNICIPIOS = str(_DATA_ROOT.joinpath("municipios_coordenadas_pixeles.json"))
TOKEN = os.getenv("NASA_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}