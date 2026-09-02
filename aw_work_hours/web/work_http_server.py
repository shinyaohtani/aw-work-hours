"""HTTPサーバー"""

import socket
import sys
import threading
import webbrowser

from .. import PROJECT_DIR
from ..domain.afk_bucket import AFKBucket
from .work_http_handler import WorkHTTPHandler
from .work_http_server_socket import WorkHTTPServerSocket


class WorkHTTPServer:
    """HTTPサーバー"""

    _WEB_DIR: str = str(PROJECT_DIR / "web")

    def __init__(self, port: int = 8600) -> None:
        self._port: int = port
        self._quiet: bool = False

    def start(self, init_month: str | None, quiet: bool, bucket: AFKBucket) -> None:
        self._quiet = quiet
        if not self._is_port_in_use():
            self._start_server(bucket)
        else:
            self._status(f"サーバーは既に起動中 (port {self._port})")
        self._open_browser(init_month)

    def _is_port_in_use(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", self._port)) == 0

    def _start_server(self, bucket: AFKBucket) -> None:
        WorkHTTPHandler.directory = self._WEB_DIR

        def serve() -> None:
            with WorkHTTPServerSocket(
                ("127.0.0.1", self._port), WorkHTTPHandler, bucket
            ) as httpd:
                httpd.serve_forever()

        threading.Thread(target=serve, daemon=True).start()
        self._status(f"サーバー起動: http://localhost:{self._port}/")

    def _open_browser(self, init_month: str | None) -> None:
        import time

        query: str = f"?month={init_month}" if init_month else ""
        url: str = f"http://localhost:{self._port}/{query}"
        self._status(f"ブラウザで開きます: {url}")
        webbrowser.open(url)
        self._status("Ctrl+C で終了")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self._status("\n終了します")

    def _status(self, msg: str) -> None:
        if not self._quiet:
            print(msg, file=sys.stderr)
