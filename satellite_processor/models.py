from pydantic import BaseModel, Field, ConfigDict
from typing import List, Tuple, Optional, Any
from datetime import date
import numpy as np

class CoordenadasPixeles(BaseModel):
    cuadrante: str = Field(..., description="Cuadrante of the image")
    coordenadas_pixeles: List[Tuple[int, int]] = Field(..., description="Coordenadas of the pixels")

class MedicionResultado(BaseModel):
    Fecha: date = Field(..., description="Date of the measurement")
    Cantidad_de_pixeles: int = Field(..., description="Number of pixels")
    Suma_de_radianza: float = Field(..., description="Sum of the radiance")
    Media_de_radianza: float = Field(..., description="Mean of the radiance")
    Desviacion_estandar_de_radianza: float = Field(..., description="Standard deviation of the radiance")
    Maximo_de_radianza: float = Field(..., description="Maximum of the radiance")
    Minimo_de_radianza: float = Field(..., description="Minimum of the radiance")
    Percentil_25_de_radianza: float = Field(..., description="25th percentile of the radiance")
    Percentil_50_de_radianza: float = Field(..., description="50th percentile of the radiance")
    Percentil_75_de_radianza: float = Field(..., description="75th percentile of the radiance")

class CoordenadasMunicipio(BaseModel):
    """Modelo para las coordenadas de un municipio"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    nombre: str = Field(..., description="Nombre del municipio")
    coordenadas: np.ndarray = Field(..., description="Coordenadas del municipio")

class ImagenProcesada(BaseModel):
    """Modelo para una imagen procesada"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    imagen_recortada: np.ndarray = Field(..., description="Imagen recortada del municipio")
    imagen_visualizacion: np.ndarray = Field(..., description="Imagen para visualización")
    coordenadas_x: np.ndarray = Field(..., description="Coordenadas X de los bordes")
    coordenadas_y: np.ndarray = Field(..., description="Coordenadas Y de los bordes")

class ResultadoProcesamiento(BaseModel):
    """Modelo para el resultado completo del procesamiento"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    medicion: MedicionResultado = Field(..., description="Mediciones de radianza")
    imagen_procesada: Optional[ImagenProcesada] = Field(None, description="Imagen procesada")
    pixeles_seleccionados: List[float] = Field(..., description="Valores de píxeles seleccionados") 