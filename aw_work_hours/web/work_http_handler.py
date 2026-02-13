"""HTTPリクエストハンドラ"""

import http.server
import json
import urllib.error
import urllib.request

from ..settings import Settings
from ..domain import AFKBucket, MonthPeriod, WorkRule
from .work_html_response import WorkHTMLResponse


class WorkHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """HTTPリクエストハンドラ"""

    directory: str = ""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, directory=self.directory, **kwargs)

    def log_message(self, format: str, *args) -> None:
        pass

    def do_GET(self) -> None:
        if self.path.startswith("/data/"):
            self._handle_data()
        elif self.path == "/settings":
            self._handle_get_settings()
        elif self.path == "/settings/buckets":
            self._handle_get_buckets()
        elif self.path.startswith("/api/"):
            self._proxy_api()
        else:
            super().do_GET()

    def do_POST(self) -> None:
        if self.path == "/settings":
            self._handle_post_settings()
        else:
            self.send_error(404)

    def _handle_get_settings(self) -> None:
        try:
            settings: Settings = Settings()
            body: bytes = json.dumps(
                {
                    "no_colon": settings.no_colon,
                    "min_event_seconds": settings.min_event_seconds,
                    "bucket": settings.bucket,
                },
                ensure_ascii=False,
            ).encode("utf-8")
            self._send_json(body)
        except Exception as e:
            self.send_error(500, f"Error: {e}")

    def _handle_get_buckets(self) -> None:
        try:
            afk_ids: list[str] = AFKBucket._fetch_ids()
            hostnames: list[str] = [
                bid.replace("aw-watcher-afk_", "") for bid in afk_ids
            ]
            body: bytes = json.dumps(hostnames, ensure_ascii=False).encode("utf-8")
            self._send_json(body)
        except Exception as e:
            self.send_error(500, f"Error: {e}")

    def _handle_post_settings(self) -> None:
        try:
            length: int = int(self.headers.get("Content-Length", 0))
            raw: bytes = self.rfile.read(length)
            data: dict[str, object] = json.loads(raw.decode("utf-8"))
            settings: Settings = Settings()
            if "no_colon" in data:
                settings.no_colon = bool(data["no_colon"])
            if "min_event_seconds" in data:
                settings.min_event_seconds = int(data["min_event_seconds"])  # type: ignore[arg-type]
            if "bucket" in data:
                settings.bucket = str(data["bucket"]) if data["bucket"] else None
            settings.save()
            WorkRule.MIN_EVENT_SECONDS = settings.min_event_seconds
            AFKBucket._cached_id = None
            AFKBucket.set_preference(settings.bucket)
            body: bytes = json.dumps(
                {
                    "no_colon": settings.no_colon,
                    "min_event_seconds": settings.min_event_seconds,
                    "bucket": settings.bucket,
                },
                ensure_ascii=False,
            ).encode("utf-8")
            self._send_json(body)
        except Exception as e:
            self.send_error(500, f"Error: {e}")

    def _handle_data(self) -> None:
        try:
            month_str: str = self.path.split("/")[-1]
            period: MonthPeriod = MonthPeriod.parse(month_str)
            response: WorkHTMLResponse = WorkHTMLResponse(period)
            body: bytes = json.dumps(response.json(), ensure_ascii=False).encode(
                "utf-8"
            )
            self._send_json(body)
        except Exception as e:
            self.send_error(500, f"Error: {e}")

    def _send_json(self, body: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _proxy_api(self) -> None:
        url: str = f"http://127.0.0.1:5600{self.path}"
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                body: bytes = resp.read()
                self._send_json(body)
        except Exception as e:
            self.send_error(502, f"API Error: {e}")
