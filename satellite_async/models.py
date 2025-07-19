from pydantic import BaseModel, Field
from typing import List, Tuple
from datetime import date

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
    