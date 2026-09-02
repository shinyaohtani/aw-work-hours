"""クライアントから送られてきた設定の差分"""

from ..settings import Settings


class SettingsPayload:
    """クライアントから送られてきた設定の差分（POST /settings のボディ）"""

    def __init__(self, raw: dict[str, object]) -> None:
        self._raw: dict[str, object] = raw

    @property
    def error(self) -> str | None:
        if "no_colon" in self._raw and not isinstance(self._raw["no_colon"], bool):
            return "no_colon must be a boolean"
        if err := self._min_event_seconds_error():
            return err
        if "bucket" in self._raw:
            v = self._raw["bucket"]
            if v is not None and not isinstance(v, str):
                return "bucket must be a string or null"
        return None

    def _min_event_seconds_error(self) -> str | None:
        if "min_event_seconds" not in self._raw:
            return None
        v = self._raw["min_event_seconds"]
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            return "min_event_seconds must be a non-negative integer"
        return None

    def apply_to(self, settings: Settings) -> None:
        if "no_colon" in self._raw and isinstance(self._raw["no_colon"], bool):
            settings.no_colon = self._raw["no_colon"]
        if "min_event_seconds" in self._raw and isinstance(
            self._raw["min_event_seconds"], int
        ):
            settings.min_event_seconds = self._raw["min_event_seconds"]
        if "bucket" in self._raw:
            bucket = self._raw["bucket"]
            settings.bucket = bucket if isinstance(bucket, str) else None
