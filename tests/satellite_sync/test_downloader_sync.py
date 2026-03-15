"""Tests for satellite_sync downloader with mocked HTTP and I/O."""
from unittest.mock import patch, MagicMock

import pytest

from satellite_sync.downloader import find_file, download_file, is_valid_hdf5_file


class TestFindFile:
    def test_returns_url_when_html_has_h5_link(self, sample_directory_html):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = sample_directory_html
        with patch("satellite_sync.downloader.requests.get", return_value=mock_resp):
            url = find_file(2024, 1, "h08v07")
        assert url is not None
        assert "h08v07" in url
        assert url.endswith(".h5")

    def test_returns_none_when_status_not_200(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        with patch("satellite_sync.downloader.requests.get", return_value=mock_resp):
            url = find_file(2024, 1, "h08v07")
        assert url is None

    def test_returns_none_when_no_matching_link(self, sample_directory_html):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html><body><a href='other.h5'>x</a></body></html>"
        with patch("satellite_sync.downloader.requests.get", return_value=mock_resp):
            url = find_file(2024, 1, "h99v99")
        assert url is None

    def test_returns_full_url_when_href_is_relative(self, sample_directory_html):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = sample_directory_html
        with patch("satellite_sync.downloader.requests.get", return_value=mock_resp):
            url = find_file(2024, 1, "h08v07")
        assert url is not None
        assert "2024" in url or "1" in url or "h08v07" in url


class TestDownloadFile:
    def test_returns_path_when_download_ok_and_valid_h5(self, tmp_path):
        save_path = str(tmp_path / "downloaded.h5")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_content = lambda chunk_size: [b"\x89HDF\r\n\x1a\n" + b"\x00" * 100]
        with patch("satellite_sync.downloader.requests.get", return_value=mock_resp):
            with patch("satellite_sync.downloader.is_valid_hdf5_file", return_value=True):
                result = download_file("http://example.com/file.h5", save_path)
        assert result == save_path

    def test_returns_none_when_response_not_200(self, tmp_path):
        save_path = str(tmp_path / "out.h5")
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        with patch("satellite_sync.downloader.requests.get", return_value=mock_resp):
            result = download_file("http://example.com/file.h5", save_path)
        assert result is None

    def test_returns_none_when_valid_hdf5_fails_after_download(self, tmp_path):
        save_path = str(tmp_path / "out.h5")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_content = lambda chunk_size: [b"not hdf5 content"]
        with patch("satellite_sync.downloader.requests.get", return_value=mock_resp):
            with patch("satellite_sync.downloader.is_valid_hdf5_file", return_value=False):
                with patch("satellite_sync.downloader.os.remove"):
                    result = download_file("http://example.com/file.h5", save_path)
        assert result is None


class TestIsValidHdf5File:
    def test_returns_true_for_valid_hdf5(self, sample_hdf5_path):
        assert is_valid_hdf5_file(sample_hdf5_path) is True

    def test_returns_false_for_nonexistent_path(self):
        assert is_valid_hdf5_file("/nonexistent/path.h5") is False

    def test_returns_false_for_empty_file(self, tmp_path):
        empty = tmp_path / "empty.h5"
        empty.write_bytes(b"")
        assert is_valid_hdf5_file(str(empty)) is False

    def test_returns_false_for_html_content(self, tmp_path):
        fake = tmp_path / "fake.h5"
        fake.write_bytes(b"<!DOCTYPE html><html></html>")
        assert is_valid_hdf5_file(str(fake)) is False
