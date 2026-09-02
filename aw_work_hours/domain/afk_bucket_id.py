"""AFKバケットの識別子"""

import json
import urllib.error
import urllib.request
from datetime import datetime

from ..types import _API_BASE, _TIMEZONE, AWEvent


class AFKBucketId:
    """AFKバケットの識別子（ホスト名を含む生のID）"""

    _PREFIX: str = "aw-watcher-afk_"

    def __init__(self, raw: str) -> None:
        self._raw: str = raw

    @property
    def raw(self) -> str:
        return self._raw

    @property
    def hostname(self) -> str:
        return self._raw.replace(self._PREFIX, "")

    @property
    def is_afk_bucket(self) -> bool:
        return self._raw.startswith(self._PREFIX)

    def matches(self, preference: str) -> bool:
        return preference.lower() in self._raw.lower()

    @property
    def last_event_at(self) -> datetime | None:
        url: str = f"{_API_BASE}/buckets/{self._raw}/events?limit=1"
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                events: list[AWEvent] = json.loads(resp.read().decode())
                if events:
                    return datetime.fromisoformat(events[0]["timestamp"]).astimezone(
                        _TIMEZONE
                    )
        except (urllib.error.URLError, KeyError, IndexError):
            # Ignore failures when fetching/parsing the last event and treat as "no data"
            pass
        return None
