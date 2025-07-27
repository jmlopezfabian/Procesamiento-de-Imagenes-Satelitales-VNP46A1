import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from config import BASE_URL, HEADERS

async def find_file(session, year, day, cuadrante):
    url = BASE_URL.format(year=year, day=day)
    async with session.get(url, headers=HEADERS) as resp:
        if resp.status != 200:
            print(f"Error al acceder a {url}")
            return None
        text = await resp.text()
        soup = BeautifulSoup(text, "html.parser")
        for link in soup.find_all("a"):
            filename = link.get("href")
            if filename and cuadrante in filename and filename.endswith(".h5"):
                return url + filename
    return None

async def download_file(session, url, path):
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=120)) as resp:
            if resp.status == 200:
                with open(path, "wb") as f:
                    while True:
                        chunk = await resp.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                return path
            print(f"Fallo la descarga del archivo: {url}")
            return None
    except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as e:
        print(f"Error al descargar {url}: {e}")
        return None