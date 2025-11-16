import os
import h5py

# URLs y rutas
BASE_URL = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5200/VNP46A1/{year}/{day}/"
IMAGE_PATH = "HDFEOS/GRIDS/VNP_Grid_DNB/Data Fields/DNB_At_Sensor_Radiance_500m"
RUTA_MUNICIPIOS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'limite-de-las-alcaldias.json')

def find_image_path(hdf_file):
    """
    Encuentra automáticamente la ruta correcta a los datos de radianza en el archivo HDF5.
    Intenta primero el path estándar, luego busca alternativas.
    """
    # Primero intentar el path estándar
    try:
        if IMAGE_PATH in hdf_file:
            return IMAGE_PATH
    except:
        pass
    
    # Si no existe, buscar en la estructura del archivo
    try:
        if 'HDFEOS' in hdf_file and 'GRIDS' in hdf_file['HDFEOS']:
            grids = hdf_file['HDFEOS']['GRIDS']
            for grid_name in grids.keys():
                grid = grids[grid_name]
                if 'Data Fields' in grid:
                    data_fields = grid['Data Fields']
                    # Buscar el campo de radianza
                    for field_name in data_fields.keys():
                        if 'Radiance' in field_name or 'DNB' in field_name:
                            path = f"HDFEOS/GRIDS/{grid_name}/Data Fields/{field_name}"
                            try:
                                if path in hdf_file:
                                    return path
                            except:
                                continue
    except Exception as e:
        print(f"Error buscando ruta alternativa en HDF5: {e}")
    
    # Si nada funciona, devolver el path por defecto
    return IMAGE_PATH

# Token de autenticación
TOKEN = os.getenv("NASA_API_TOKEN")

# Headers para requests
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Configuración de procesamiento
CHUNK_SIZE = 8192
CONVERSION_FACTOR = 1_000_000 