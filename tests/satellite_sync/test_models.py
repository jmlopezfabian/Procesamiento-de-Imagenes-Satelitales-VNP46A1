"""Unit tests for satellite_sync Pydantic models."""
import pytest
from datetime import date
from pydantic import ValidationError

from satellite_sync.models import CoordenadasPixeles, MedicionResultado


class TestCoordenadasPixeles:
    def test_valid_coordenadas_pixeles(self):
        data = {
            "cuadrante": "h08v07",
            "coordenadas_pixeles": [(0, 0), (1, 1), (2, 2)],
        }
        obj = CoordenadasPixeles(**data)
        assert obj.cuadrante == "h08v07"
        assert obj.coordenadas_pixeles == [(0, 0), (1, 1), (2, 2)]

    def test_missing_cuadrante_raises(self):
        with pytest.raises(ValidationError):
            CoordenadasPixeles(coordenadas_pixeles=[(0, 0)])

    def test_missing_coordenadas_pixeles_raises(self):
        with pytest.raises(ValidationError):
            CoordenadasPixeles(cuadrante="h08v07")

    def test_empty_coordenadas_pixeles_allowed(self):
        obj = CoordenadasPixeles(cuadrante="h09v07", coordenadas_pixeles=[])
        assert obj.coordenadas_pixeles == []


class TestMedicionResultado:
    def test_valid_medicion_resultado(self):
        data = {
            "Fecha": date(2024, 1, 1),
            "Cantidad_de_pixeles": 100,
            "Cantidad_de_pixeles_principales": 80,
            "Suma_de_radianza": 500.0,
            "Media_de_radianza": 5.0,
            "Desviacion_estandar_de_radianza": 2.0,
            "Maximo_de_radianza": 10.0,
            "Minimo_de_radianza": 0.5,
            "Percentil_25_de_radianza": 3.0,
            "Percentil_50_de_radianza": 5.0,
            "Percentil_75_de_radianza": 7.0,
        }
        obj = MedicionResultado(**data)
        assert obj.Fecha == date(2024, 1, 1)
        assert obj.Cantidad_de_pixeles == 100
        assert obj.Media_de_radianza == 5.0
        assert obj.Maximo_de_radianza == 10.0

    def test_dict_export(self):
        data = {
            "Fecha": date(2024, 1, 15),
            "Cantidad_de_pixeles": 50,
            "Cantidad_de_pixeles_principales": 50,
            "Suma_de_radianza": 250.0,
            "Media_de_radianza": 5.0,
            "Desviacion_estandar_de_radianza": 1.0,
            "Maximo_de_radianza": 8.0,
            "Minimo_de_radianza": 2.0,
            "Percentil_25_de_radianza": 4.0,
            "Percentil_50_de_radianza": 5.0,
            "Percentil_75_de_radianza": 6.0,
        }
        obj = MedicionResultado(**data)
        d = obj.model_dump()
        assert "Fecha" in d
        assert "Media_de_radianza" in d
        assert d["Cantidad_de_pixeles"] == 50

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            MedicionResultado(
                Fecha=date(2024, 1, 1),
                Cantidad_de_pixeles=10,
                # missing Cantidad_de_pixeles_principales and others
            )

    def test_invalid_type_raises(self):
        with pytest.raises(ValidationError):
            MedicionResultado(
                Fecha="not-a-date",
                Cantidad_de_pixeles=10,
                Cantidad_de_pixeles_principales=10,
                Suma_de_radianza=1.0,
                Media_de_radianza=1.0,
                Desviacion_estandar_de_radianza=0.0,
                Maximo_de_radianza=1.0,
                Minimo_de_radianza=0.0,
                Percentil_25_de_radianza=0.0,
                Percentil_50_de_radianza=0.0,
                Percentil_75_de_radianza=0.0,
            )
