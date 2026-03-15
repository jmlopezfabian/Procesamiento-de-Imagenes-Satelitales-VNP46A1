"""Integration tests for satellite_async processing with mocked HDF5."""
from datetime import date

import pytest

from satellite_async.processing import process_image


class TestProcessImage:
    def test_returns_medicion_resultado_when_path_valid(self, sample_hdf5_path):
        # Coordinates within 10x10 fixture image
        coords = [(1, 1), (2, 1), (2, 2), (1, 2)]
        result = process_image(
            sample_hdf5_path,
            coords,
            date(2024, 1, 1),
            "Iztapalapa",
            delete_file=False,
        )
        assert result is not None
        assert result.Municipio == "Iztapalapa"
        assert result.Fecha == date(2024, 1, 1)
        assert result.Cantidad_de_pixeles == len(coords)
        assert result.Suma_de_radianza >= 0
        assert result.Media_de_radianza >= 0

    def test_returns_none_when_path_does_not_exist(self):
        result = process_image(
            "/nonexistent/path.h5",
            [(0, 0)],
            date(2024, 1, 1),
            "Test",
            delete_file=False,
        )
        assert result is None

    def test_returns_none_when_no_valid_coordinates(self, sample_hdf5_path):
        # Coordinates outside 10x10 image
        coords = [(100, 100), (101, 101)]
        result = process_image(
            sample_hdf5_path,
            coords,
            date(2024, 1, 1),
            "Test",
            delete_file=False,
        )
        assert result is None

    def test_returns_none_when_empty_coordinates(self, sample_hdf5_path):
        result = process_image(
            sample_hdf5_path,
            [],
            date(2024, 1, 1),
            "Test",
            delete_file=False,
        )
        assert result is None
