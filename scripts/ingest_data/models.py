from sqlalchemy import Integer, Float, Column, String, ForeignKey, Date
from sqlalchemy import DeclarativeBase
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

Base = DeclarativeBase

class Municipio(Base):
    __tablename__ = "municipio"

    id = Column(Integer, primary_key=True)
    nombre = Column(String)

    coordenadas = relationship("CoordendasMunicipio", back_populates="Municipio")
    radianza = relationship("RadianzaMunicipios", back_populates="Municipio")

class CoordendasMunicipio(Base):
    __tablename__ = "coordenadas_municipio"

    id = Column(Integer, primary_key=True)
    id_municipio = Column(Integer, ForeignKey("municipio.id"))
    coordenadas_lat_lon = Column(ARRAY(Float))
    coordenadas_pixel = Column(ARRAY(Float))

    municipio = relationship("Municipio", back_populates="CoordendasMunicipio")

class RadianzaMunicipios(Base):
    __tablename__ = "radianza_municipios"

    id = Column(Integer, primary_key=True)
    id_municipio = Column(Integer, ForeignKey("municipio.id"))
    fecha = Column(Date)
    suma_radianza = Column(Float)
    media_radianza = Column(Float)
    desviacion_estandar_radianza = Column(Float)
    maximo_radianza = Column(Float)
    minimo_radianza = Column(Float)
    percentil_25_radianza = Column(Float)
    percentil_50_radianza = Column(Float)
    percentil_75_radianza = Column(Float)

    municipio = relationship("Municipio", back_populates="RadianzaMunicipios")
