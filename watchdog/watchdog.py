from typing import Literal

from .functor import Functor
import subprocess
import socket
import requests
import requests
import asyncio
import platform
import aiohttp

from .data.watchdog import Watchdog as Data

class Watchdog(Functor[None]):
        
    def __init__(self, data:Data):
        self._data = data
    
    async def run(self) -> None:
        method = self._data.test_method
        func = getattr(self, f"_run_{method}", None)
        if func is not None:
            await func()
        else:
            raise ValueError(f"Unknown test method: {self._data.test_method}")

    async def _run_ping(self):
        # Use system ping asynchronously
        try:
            ping_cmd = ["ping", "-n" if platform.system() == "Windows" else "-c", "1", self._data.address]
            proc = await asyncio.create_subprocess_exec(
                *ping_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, _ = await proc.communicate()
            if proc.returncode == 0:
                print(f"Ping to {self._data.address} succeeded.")
            else:
                print(f"Ping to {self._data.address} failed.")
        except Exception as e:
            print(f"Ping error: {e}")

    async def _run_tcp(self):
        try:
            reader, writer = await asyncio.open_connection(self._data.address, self._data.port)
            print(f"TCP connection to {self._data.address}:{self._data.port} succeeded.")
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            print(f"TCP connection to {self._data.address}:{self._data.port} failed: {e}")

    async def _run_http(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{self._data.address}:{self._data.port}", timeout=5) as response:
                    print(f"HTTP GET {self._data.address}:{self._data.port} status: {response.status}")
        except Exception as e:
            print(f"HTTP request failed: {e}")

    async def _run_https(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://{self._data.address}:{self._data.port}", timeout=5) as response:
                    print(f"HTTPS GET {self._data.address}:{self._data.port} status: {response.status}")
        except Exception as e:
            print(f"HTTPS request failed: {e}")