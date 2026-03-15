"""Unit tests for satellite_sync utils (pure functions and I/O with mocks)."""
import json
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import numpy as np
import pytest

from satellite_sync.utils import (
    normalize_municipio,
    parse_date,
    distancia_puntos,
    polygon_centroid,
    es_borde,
    extraer_coordenadas,
    load_coord_data,
    left_right_coords,
)


# --- Pure functions (no I/O) ---


class TestNormalizeMunicipio:
    def test_lowercase(self):
        assert normalize_municipio("Iztapalapa") == "iztapalapa"

    def test_removes_accents(self):
        assert normalize_municipio("Álvaro") == "alvaro"
        assert normalize_municipio("México") == "mexico"
        assert "ó" not in normalize_municipio("ó")


class TestParseDate:
    def test_parse_valid_date(self):
        year, day, date_obj = parse_date("01-01-24")
        assert year == 2024
        assert day == 1
        assert date_obj.year == 2024 and date_obj.month == 1 and date_obj.day == 1

    def test_parse_mid_year(self):
        year, day, date_obj = parse_date("15-06-23")
        assert year == 2023
        assert date_obj.month == 6 and date_obj.day == 15

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            parse_date("2024-01-01")


class TestDistanciaPuntos:
    def test_same_point(self):
        assert distancia_puntos((1.0, 2.0), (1.0, 2.0)) == 0.0

    def test_horizontal_distance(self):
        d = distancia_puntos((0.0, 0.0), (3.0, 0.0))
        assert d == pytest.approx(3.0)

    def test_diagonal_distance(self):
        d = distancia_puntos((0.0, 0.0), (3.0, 4.0))
        assert d == pytest.approx(5.0)


class TestPolygonCentroid:
    def test_square_centroid(self):
        # Unit square
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        cx, cy = polygon_centroid(vertices)
        assert cx == pytest.approx(0.5)
        assert cy == pytest.approx(0.5)

    def test_triangle_centroid(self):
        vertices = [(0, 0), (2, 0), (1, 2)]
        cx, cy = polygon_centroid(vertices)
        assert cx == pytest.approx(1.0)
        assert cy == pytest.approx(2.0 / 3.0)


class TestEsBorde:
    def test_point_on_border(self):
        bordes = [(0, 0), (1, 0), (1, 1)]
        assert es_borde(1, 0, bordes) is True

    def test_point_not_on_border(self):
        bordes = [(0, 0), (1, 0), (1, 1)]
        assert es_borde(5, 5, bordes) is False


# --- I/O with mocks ---


class TestExtraerCoordenadas:
    def test_returns_coordinates_when_found(self, municipios_json_path):
        with patch("satellite_sync.utils.RUTA_MUNICIPIOS", municipios_json_path):
            coords = extraer_coordenadas("Iztapalapa")
        assert coords is not None
        assert isinstance(coords, np.ndarray)
        assert len(coords) > 0

    def test_returns_none_when_not_found(self, municipios_json_path):
        with patch("satellite_sync.utils.RUTA_MUNICIPIOS", municipios_json_path):
            coords = extraer_coordenadas("MunicipioInexistente")
        assert coords is None

    def test_returns_none_on_invalid_json(self):
        with patch("satellite_sync.utils.RUTA_MUNICIPIOS", "/nonexistent/path.json"):
            with patch("builtins.open", mock_open(read_data="invalid {")):
                coords = extraer_coordenadas("Iztapalapa")
        assert coords is None


class TestLoadCoordData:
    def test_loads_coordenadas_pixeles(self, tmp_path):
        path = tmp_path / "coords.json"
        path.write_text(
            json.dumps({
                "Iztapalapa": {
                    "cuadrante": "h08v07",
                    "coordenadas_pixeles": [(10, 20), (11, 21)],
                }
            }),
            encoding="utf-8",
        )
        obj = load_coord_data("Iztapalapa", str(path))
        assert obj.cuadrante == "h08v07"
        assert obj.coordenadas_pixeles == [(10, 20), (11, 21)]


class TestLeftRightCoords:
    def test_extracts_upper_left_lower_right(self):
        meta = (
            "UpperLeftPointMtrs=(-1111950.519723,-555975.259861)\n"
            "LowerRightMtrs=(-1000755.467751,-666300.346481)\n"
        )
        # Value that supports .tobytes().decode("utf-8") as in utils
        meta_val = np.array(meta, dtype="S" + str(len(meta) + 1)).flat[0]
        mock_ds = MagicMock()
        mock_ds.__getitem__.return_value = meta_val
        mock_file = MagicMock()
        mock_file.__getitem__.return_value = mock_ds
        left, right = left_right_coords(mock_file)
        assert left is not None
        assert right is not None
        assert left[0] == pytest.approx(-1.111950519723)
        assert right[0] == pytest.approx(-1.000755467751)

    def test_returns_none_when_metadata_missing(self):
        mock_file = MagicMock()
        mock_file.__getitem__ = MagicMock(side_effect=KeyError("no metadata"))
        left, right = left_right_coords(mock_file)
        assert left is None
        assert right is None
