"""
Satellite Processor - Sistema modular para procesamiento de imágenes satelitales VNP46A1

Este paquete proporciona funcionalidades para:
- Descarga de imágenes satelitales desde NASA
- Procesamiento y recorte de imágenes por municipio
- Extracción de mediciones de radianza
- Visualización de resultados

Módulos principales:
- config: Configuración y constantes
- models: Modelos de datos con Pydantic
- utils: Funciones auxiliares
- downloader: Descarga de archivos
- image_processor: Procesamiento de imágenes
- processor: Clase principal SatelliteProcessor
"""

from processor import SatelliteProcessor
from models import (
    CoordenadasPixeles,
    MedicionResultado,
    CoordenadasMunicipio,
    ImagenProcesada,
    ResultadoProcesamiento
)
from utils import (
    normalize_municipio,
    parse_date,
    extraer_coordenadas,
    left_right_coords,
    polygon_centroid
)
from downloader import find_file, download_file
from image_processor import (
    recortar_imagen,
    completar_bordes,
    get_pixeles,
    aumentar_imagen
)

__version__ = "1.0.0"
__author__ = "Tu Nombre"

__all__ = [
    "SatelliteProcessor",
    "CoordenadasPixeles",
    "MedicionResultado",
    "CoordenadasMunicipio",
    "ImagenProcesada",
    "ResultadoProcesamiento",
    "normalize_municipio",
    "parse_date",
    "extraer_coordenadas",
    "left_right_coords",
    "polygon_centroid",
    "find_file",
    "download_file",
    "recortar_imagen",
    "completar_bordes",
    "get_pixeles",
    "aumentar_imagen"
]