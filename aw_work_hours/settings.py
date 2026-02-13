"""永続化設定"""

import json
from pathlib import Path


class Settings:
    """永続化設定（settings.json）"""

    _PATH: Path = Path.home() / ".config" / "aw-work-hours" / "settings.json"

    def __init__(self) -> None:
        self._data: dict[str, object] = self._load()

    def _load(self) -> dict[str, object]:
        try:
            with open(self._PATH, encoding="utf-8") as f:
                result: dict[str, object] = json.load(f)
                return result
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save(self) -> None:
        self._PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self._PATH, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    @property
    def no_colon(self) -> bool:
        return bool(self._data.get("no_colon", False))

    @no_colon.setter
    def no_colon(self, value: bool) -> None:
        self._data["no_colon"] = value

    @property
    def min_event_seconds(self) -> int:
        v: object = self._data.get("min_event_seconds", 150)
        return int(v) if isinstance(v, (int, float, str)) else 150

    @min_event_seconds.setter
    def min_event_seconds(self, value: int) -> None:
        self._data["min_event_seconds"] = value

    @property
    def bucket(self) -> str | None:
        v: object = self._data.get("bucket")
        return str(v) if v is not None else None

    @bucket.setter
    def bucket(self, value: str | None) -> None:
        self._data["bucket"] = value
