"""Integration tests for satellite_sync processor with mocked download and I/O."""
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd
import pytest

from satellite_sync.processor import SatelliteProcessor


def _fake_recortar(image_matrix, coords, upper_left, factor_escala):
    """Return small image and border coords that avoid division by zero in completar_bordes."""
    small = np.ones((5, 5), dtype=np.float32) * 10.0
    # Border coords with no vertical segment (all x different)
    nx = np.array([0.5, 1.5, 2.0, 1.0])
    ny = np.array([0.5, 0.5, 1.5, 1.5])
    return small, nx, ny


def _fake_completar_bordes(nx, ny):
    return [(0, 0), (1, 0), (2, 1), (1, 1), (0, 0)]


def _fake_get_pixeles(imagen, centroide, bordes):
    return [(1, 1), (2, 1), (1, 2)]


def _fake_detect_orphan(imagen, bordes, main_pixels):
    return []


class TestSatelliteProcessor:
    def test_get_measures_returns_dict_when_mocks_ok(self, sample_hdf5_path):
        coords = np.array([[-1.05, -0.60], [-1.04, -0.59], [-1.045, -0.58], [-1.05, -0.60]])
        with patch("satellite_sync.processor.find_file", return_value="http://example.com/file.h5"):
            with patch("satellite_sync.processor.download_file", return_value=sample_hdf5_path):
                with patch("satellite_sync.processor.extraer_coordenadas", return_value=coords):
                    with patch("satellite_sync.processor.recortar_imagen", side_effect=_fake_recortar):
                        with patch("satellite_sync.processor.completar_bordes", side_effect=_fake_completar_bordes):
                            with patch("satellite_sync.processor.get_pixeles", side_effect=_fake_get_pixeles):
                                with patch("satellite_sync.processor.detect_orphan_pixels", side_effect=_fake_detect_orphan):
                                    proc = SatelliteProcessor("Iztapalapa")
                                    result = proc.get_measures("01-01-24", "h08v07", show_plots=False)
        assert result is not None
        assert isinstance(result, dict)
        assert "Fecha" in result
        assert "Cantidad_de_pixeles" in result
        assert "Media_de_radianza" in result
        assert "Suma_de_radianza" in result

    def test_get_measures_returns_none_when_find_file_fails(self):
        with patch("satellite_sync.processor.find_file", return_value=None):
            proc = SatelliteProcessor("Iztapalapa")
            result = proc.get_measures("01-01-24", "h08v07", show_plots=False)
        assert result is None

    def test_get_measures_returns_none_when_download_fails(self):
        with patch("satellite_sync.processor.find_file", return_value="http://example.com/file.h5"):
            with patch("satellite_sync.processor.download_file", return_value=None):
                proc = SatelliteProcessor("Iztapalapa")
                result = proc.get_measures("01-01-24", "h08v07", show_plots=False)
        assert result is None

    def test_get_measures_returns_none_when_extraer_coordenadas_fails(self, sample_hdf5_path):
        with patch("satellite_sync.processor.find_file", return_value="http://example.com/file.h5"):
            with patch("satellite_sync.processor.download_file", return_value=sample_hdf5_path):
                with patch("satellite_sync.processor.extraer_coordenadas", return_value=None):
                    proc = SatelliteProcessor("Iztapalapa")
                    result = proc.get_measures("01-01-24", "h08v07", show_plots=False)
        assert result is None

    def test_run_accumulates_results_in_dataframe(self, sample_hdf5_path):
        coords = np.array([[-1.05, -0.60], [-1.04, -0.59], [-1.045, -0.58], [-1.05, -0.60]])
        with patch("satellite_sync.processor.find_file", return_value="http://example.com/file.h5"):
            with patch("satellite_sync.processor.download_file", return_value=sample_hdf5_path):
                with patch("satellite_sync.processor.extraer_coordenadas", return_value=coords):
                    with patch("satellite_sync.processor.recortar_imagen", side_effect=_fake_recortar):
                        with patch("satellite_sync.processor.completar_bordes", side_effect=_fake_completar_bordes):
                            with patch("satellite_sync.processor.get_pixeles", side_effect=_fake_get_pixeles):
                                with patch("satellite_sync.processor.detect_orphan_pixels", side_effect=_fake_detect_orphan):
                                    with patch("satellite_sync.processor.os.remove"):
                                        proc = SatelliteProcessor("Iztapalapa")
                                        df = proc.run(["01-01-24", "02-01-24"], "h08v07", show_plots=False)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "Fecha" in df.columns
        assert "Media_de_radianza" in df.columns

    def test_run_returns_empty_dataframe_when_no_results(self):
        with patch("satellite_sync.processor.find_file", return_value=None):
            proc = SatelliteProcessor("Iztapalapa")
            df = proc.run(["01-01-24", "02-01-24"], "h08v07", show_plots=False)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
