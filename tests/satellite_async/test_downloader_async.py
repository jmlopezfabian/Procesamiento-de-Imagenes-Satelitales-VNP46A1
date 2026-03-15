"""Tests for satellite_async downloader with mocked HTTP."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from satellite_async.downloader import find_file, download_file


def _make_resp(status=200, text="", content_bytes=None):
    resp = MagicMock()
    resp.status = status
    resp.text = AsyncMock(return_value=text)
    if content_bytes is not None:
        resp.content.read = AsyncMock(side_effect=[content_bytes, b""])
    else:
        resp.content.read = AsyncMock(return_value=b"")
    return resp


@pytest.mark.asyncio
class TestFindFileAsync:
    async def test_returns_url_when_html_has_h5_link(self, sample_directory_html):
        session = MagicMock()
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=_make_resp(200, sample_directory_html))
        ctx.__aexit__ = AsyncMock(return_value=None)
        session.get = MagicMock(return_value=ctx)
        url = await find_file(session, 2024, 1, "h08v07")
        assert url is not None
        assert "h08v07" in url
        assert url.endswith(".h5")

    async def test_returns_none_when_status_not_200(self):
        session = MagicMock()
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=_make_resp(404, ""))
        ctx.__aexit__ = AsyncMock(return_value=None)
        session.get = MagicMock(return_value=ctx)
        url = await find_file(session, 2024, 1, "h08v07")
        assert url is None

    async def test_returns_none_when_no_matching_link(self):
        session = MagicMock()
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(
            return_value=_make_resp(200, "<html><body><a href='other.h5'>x</a></body></html>")
        )
        ctx.__aexit__ = AsyncMock(return_value=None)
        session.get = MagicMock(return_value=ctx)
        url = await find_file(session, 2024, 1, "h99v99")
        assert url is None


@pytest.mark.asyncio
class TestDownloadFileAsync:
    async def test_returns_path_when_download_ok(self, tmp_path):
        path = str(tmp_path / "out.h5")
        session = MagicMock()
        ctx = MagicMock()
        resp = _make_resp(200, "", content_bytes=b"binary content here")
        ctx.__aenter__ = AsyncMock(return_value=resp)
        ctx.__aexit__ = AsyncMock(return_value=None)
        session.get = MagicMock(return_value=ctx)
        result = await download_file(session, "http://example.com/file.h5", path)
        assert result == path
        assert (tmp_path / "out.h5").read_bytes() == b"binary content here"

    async def test_returns_none_when_status_not_200(self, tmp_path):
        path = str(tmp_path / "out.h5")
        session = MagicMock()
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=_make_resp(404, ""))
        ctx.__aexit__ = AsyncMock(return_value=None)
        session.get = MagicMock(return_value=ctx)
        result = await download_file(session, "http://example.com/file.h5", path)
        assert result is None
