"""ActivityWatch APIへのプロキシ"""

import urllib.request


class ActivityWatchProxy:
    """ActivityWatch APIへのプロキシ"""

    def __init__(self, path: str) -> None:
        self._path: str = path

    @property
    def response_body(self) -> bytes:
        url: str = f"http://127.0.0.1:5600{self._path}"
        with urllib.request.urlopen(url, timeout=30) as resp:
            return resp.read()
