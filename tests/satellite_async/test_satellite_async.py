"""Integration tests for satellite_async SatelliteImagesAsync with mocked download/processing."""
from datetime import date
from unittest.mock import patch, AsyncMock, MagicMock

import pandas as pd
import pytest

from satellite_async.satellite_async import SatelliteImagesAsync


@pytest.fixture
def mock_coord_data():
    """Fake CoordenadasPixeles-like object for init."""
    obj = MagicMock()
    obj.cuadrante = "h08v07"
    obj.coordenadas_pixeles = [(1, 1), (2, 1), (2, 2), (1, 2)]
    return obj


@pytest.mark.asyncio
class TestSatelliteImagesAsyncRun:
    async def test_run_returns_dataframe_with_results(self, mock_coord_data):
        with patch("satellite_async.satellite_async.load_coord_data", return_value=mock_coord_data):
            sat = SatelliteImagesAsync("Iztapalapa")
        fake_results = [
            {
                "Fecha": date(2024, 1, 1),
                "Municipio": "iztapalapa",
                "Cantidad_de_pixeles": 4,
                "Suma_de_radianza": 10.0,
                "Media_de_radianza": 2.5,
                "Desviacion_estandar_de_radianza": 0.5,
                "Maximo_de_radianza": 3.0,
                "Minimo_de_radianza": 2.0,
                "Percentil_25_de_radianza": 2.0,
                "Percentil_50_de_radianza": 2.5,
                "Percentil_75_de_radianza": 3.0,
            }
        ]
        with patch.object(
            sat,
            "get_measures_for_date",
            new_callable=AsyncMock,
            return_value=fake_results,
        ):
            df = await sat.run(["01-01-24"])
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert "Municipio" in df.columns
        assert "Media_de_radianza" in df.columns

    async def test_run_aggregates_multiple_dates(self, mock_coord_data):
        with patch("satellite_async.satellite_async.load_coord_data", return_value=mock_coord_data):
            sat = SatelliteImagesAsync("Iztapalapa")
        with patch.object(
            sat,
            "get_measures_for_date",
            new_callable=AsyncMock,
            side_effect=[
                [{"Fecha": date(2024, 1, 1), "Municipio": "iztapalapa", "Cantidad_de_pixeles": 1, "Suma_de_radianza": 1.0, "Media_de_radianza": 1.0, "Desviacion_estandar_de_radianza": 0.0, "Maximo_de_radianza": 1.0, "Minimo_de_radianza": 1.0, "Percentil_25_de_radianza": 1.0, "Percentil_50_de_radianza": 1.0, "Percentil_75_de_radianza": 1.0}],
                [{"Fecha": date(2024, 1, 2), "Municipio": "iztapalapa", "Cantidad_de_pixeles": 2, "Suma_de_radianza": 2.0, "Media_de_radianza": 1.0, "Desviacion_estandar_de_radianza": 0.0, "Maximo_de_radianza": 1.0, "Minimo_de_radianza": 1.0, "Percentil_25_de_radianza": 1.0, "Percentil_50_de_radianza": 1.0, "Percentil_75_de_radianza": 1.0}],
            ],
        ):
            df = await sat.run(["01-01-24", "02-01-24"], save_progress_enabled=False)
        assert len(df) == 2

    async def test_run_returns_empty_dataframe_when_no_results(self, mock_coord_data):
        with patch("satellite_async.satellite_async.load_coord_data", return_value=mock_coord_data):
            sat = SatelliteImagesAsync("Iztapalapa")
        with patch.object(
            sat,
            "get_measures_for_date",
            new_callable=AsyncMock,
            return_value=[],
        ):
            df = await sat.run(["01-01-24"], save_progress_enabled=False)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
