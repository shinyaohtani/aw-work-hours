"""HTTPサーバー"""

import http.server
import socket
import sys
import threading
import webbrowser

from .. import PROJECT_DIR
from .work_http_handler import WorkHTTPHandler


class WorkHTTPServer:
    """HTTPサーバー"""

    _WEB_DIR: str = str(PROJECT_DIR / "web")

    def __init__(self, port: int = 8600) -> None:
        self._port: int = port

    def start(self, init_month: str | None, quiet: bool) -> None:
        if not self._is_port_in_use():
            self._start_server(quiet)
        else:
            self._status(f"サーバーは既に起動中 (port {self._port})", quiet)
        self._open_browser(init_month, quiet)

    def _is_port_in_use(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", self._port)) == 0

    def _start_server(self, quiet: bool) -> None:
        WorkHTTPHandler.directory = self._WEB_DIR

        def serve() -> None:
            with http.server.HTTPServer(("127.0.0.1", self._port), WorkHTTPHandler) as httpd:
                httpd.serve_forever()

        threading.Thread(target=serve, daemon=True).start()
        self._status(f"サーバー起動: http://localhost:{self._port}/", quiet)

    def _open_browser(self, init_month: str | None, quiet: bool) -> None:
        import time

        query: str = f"?month={init_month}" if init_month else ""
        url: str = f"http://localhost:{self._port}/{query}"
        self._status(f"ブラウザで開きます: {url}", quiet)
        webbrowser.open(url)
        self._status("Ctrl+C で終了", quiet)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self._status("\n終了します", quiet)

    def _status(self, msg: str, quiet: bool) -> None:
        if not quiet:
            print(msg, file=sys.stderr)
