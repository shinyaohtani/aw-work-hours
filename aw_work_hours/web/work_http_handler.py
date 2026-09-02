"""HTTPリクエストハンドラ"""

import http.server
import json
from typing import Any

from ..settings import Settings
from ..domain.afk_bucket import AFKBucket
from ..domain.month_period import MonthPeriod
from ..domain.work_rule import WorkRule
from .activity_watch_proxy import ActivityWatchProxy
from .settings_payload import SettingsPayload
from .work_html_response import WorkHTMLResponse


class WorkHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """HTTPリクエストハンドラ"""

    directory: str = ""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=self.directory, **kwargs)

    def log_message(self, format: str, *args) -> None:
        pass

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

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
            body: bytes = json.dumps(Settings().as_dict, ensure_ascii=False).encode(
                "utf-8"
            )
            self._send_json(body)
        except Exception as e:
            self.send_error(500, f"Error: {e}")

    def _handle_get_buckets(self) -> None:
        try:
            hostnames: list[str] = [b.hostname for b in AFKBucket.fetch_ids()]
            body: bytes = json.dumps(hostnames, ensure_ascii=False).encode("utf-8")
            self._send_json(body)
        except Exception as e:
            self.send_error(500, f"Error: {e}")

    def _handle_post_settings(self) -> None:
        try:
            length: int = int(self.headers.get("Content-Length", 0))
            raw: dict[str, object] = json.loads(self.rfile.read(length).decode("utf-8"))
            payload: SettingsPayload = SettingsPayload(raw)
            if payload.error:
                self.send_error(400, payload.error)
                return
            settings: Settings = Settings()
            payload.apply_to(settings)
            settings.save()
            WorkRule.MIN_EVENT_SECONDS = settings.min_event_seconds
            AFKBucket.clear_cache()
            AFKBucket.set_preference(settings.bucket)
            body: bytes = json.dumps(settings.as_dict, ensure_ascii=False).encode(
                "utf-8"
            )
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
        try:
            self._send_json(ActivityWatchProxy(self.path).response_body)
        except Exception as e:
            self.send_error(502, f"API Error: {e}")
