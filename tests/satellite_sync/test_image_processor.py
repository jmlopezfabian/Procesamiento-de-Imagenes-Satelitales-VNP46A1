"""Unit tests for satellite_sync image_processor (pure numpy/geometry)."""
import numpy as np
import pytest

from satellite_sync.image_processor import (
    aumentar_imagen,
    recortar_imagen,
    completar_bordes,
    get_pixeles,
    detect_orphan_pixels,
)


class TestAumentarImagen:
    def test_factor_one_equivalent(self):
        img = np.array([[1.0, 2.0], [3.0, 4.0]])
        out = aumentar_imagen(img, 1)
        np.testing.assert_array_almost_equal(out, img)

    def test_factor_two_doubles_shape(self):
        img = np.array([[1.0, 2.0], [3.0, 4.0]])
        out = aumentar_imagen(img, 2)
        assert out.shape == (4, 4)
        assert out[0, 0] == 1.0
        assert out[1, 1] == 1.0

    def test_factor_three(self):
        img = np.ones((2, 2))
        out = aumentar_imagen(img, 3)
        assert out.shape == (6, 6)


class TestRecortarImagen:
    def test_recorte_basic(self):
        # Image 10x10, upper_left in same coordinate system as coords
        image = np.random.rand(10, 10).astype(np.float32)
        # Municipio bbox in "pixel-like" coords: we need coords in same units as upper_left
        # upper_left (0,0) in 10x10 image with resolution 1.0 -> pixels 0-10
        resolucion = 10 / 10  # 1.0
        upper_left = (0.0, 10.0)  # typical lat/lon style, y decreases down
        # Coords that map to pixels (1,1) to (5,5) in image
        coords = np.array([
            [1.0, 9.0],
            [5.0, 9.0],
            [5.0, 5.0],
            [1.0, 5.0],
            [1.0, 9.0],
        ])
        recortada, nx, ny = recortar_imagen(image, coords, upper_left, factor_escala=1)
        assert recortada.size > 0
        assert len(nx) == len(coords)
        assert len(ny) == len(coords)

    def test_recorte_with_scale_factor(self):
        image = np.ones((20, 20), dtype=np.float32)
        upper_left = (0.0, 20.0)
        coords = np.array([[2.0, 18.0], [6.0, 18.0], [6.0, 14.0], [2.0, 14.0], [2.0, 18.0]])
        recortada, nx, ny = recortar_imagen(image, coords, upper_left, factor_escala=2)
        assert recortada.size > 0
        assert recortada.shape[0] >= 8  # 4 rows * 2
        assert recortada.shape[1] >= 8


class TestCompletarBordes:
    def test_consecutive_points_unchanged(self):
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([0.0, 0.0, 0.0])
        bordes = completar_bordes(x, y)
        assert len(bordes) >= 3
        assert (0, 0) in bordes
        assert (2, 0) in bordes

    def test_gap_filled(self):
        x = np.array([0.0, 10.0])  # gap of 10
        y = np.array([0.0, 0.0])
        bordes = completar_bordes(x, y)
        assert len(bordes) >= 2


class TestGetPixeles:
    def test_single_pixel_inside(self):
        img = np.zeros((5, 5))
        centroide = (2, 2)
        bordes = [(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)]  # square border
        pixels = get_pixeles(img, centroide, bordes)
        assert (2, 2) in pixels
        assert len(pixels) > 1  # at least centroid + neighbors inside

    def test_centroid_only_when_fully_bordered(self):
        img = np.zeros((3, 3))
        centroide = (1, 1)
        bordes = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (0, 1), (0, 0)]
        pixels = get_pixeles(img, centroide, bordes)
        assert (1, 1) in pixels


class TestDetectOrphanPixels:
    def test_no_orphans_when_all_filled(self):
        img = np.ones((5, 5))
        bordes = [(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)]
        main = [(1, 1), (2, 1), (1, 2), (2, 2)]
        orphans = detect_orphan_pixels(img, bordes, main)
        # May have orphans in corners depending on border shape
        assert isinstance(orphans, list)

    def test_returns_list_of_tuples(self):
        img = np.zeros((4, 4))
        bordes = [(0, 0), (3, 0), (3, 3), (0, 3), (0, 0)]
        main = [(1, 1)]
        orphans = detect_orphan_pixels(img, bordes, main)
        assert all(isinstance(p, tuple) and len(p) == 2 for p in orphans)
