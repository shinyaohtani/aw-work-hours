"""ActivityWatchのAFKイベント"""

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from ..types import _API_BASE, _TIMEZONE, APIConnectionError, AWEvent
from .afk_bucket import AFKBucket
from .work_rule import WorkRule


class AFKEvents:
    """ActivityWatchのAFKイベント"""

    def __init__(self, events: list[AWEvent]) -> None:
        self._events: list[AWEvent] = events

    @classmethod
    def fetch(cls, start: str | None, end: str | None) -> "AFKEvents":
        url: str = f"{_API_BASE}/buckets/{AFKBucket.id()}/events"
        params: dict[str, str] = {"limit": "-1"}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        url += "?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                return cls(json.loads(resp.read().decode()))
        except urllib.error.URLError as e:
            raise APIConnectionError(
                "エラー: ActivityWatch APIに接続できません\n"
                "ActivityWatchが起動しているか確認してください\n"
                f"詳細: {e}"
            ) from e

    @property
    def raw(self) -> list[AWEvent]:
        return self._events

    @property
    def work_blocks(self) -> list[tuple[datetime, datetime]]:
        not_afk: list[AWEvent] = sorted(
            [
                e
                for e in self._events
                if e["data"]["status"] == "not-afk"
                and e["duration"] >= WorkRule.MIN_EVENT_SECONDS
            ],
            key=lambda e: e["timestamp"],
        )
        return self._extract_blocks(not_afk) if not_afk else []

    def _extract_blocks(self, events: list[AWEvent]) -> list[tuple[datetime, datetime]]:
        blocks: list[tuple[datetime, datetime]] = []
        block_start: datetime | None = None
        block_end: datetime = datetime.min.replace(tzinfo=_TIMEZONE)
        for event in events:
            start: datetime = datetime.fromisoformat(event["timestamp"]).astimezone(
                _TIMEZONE
            )
            end: datetime = start + timedelta(seconds=event["duration"])
            if block_start is None:
                block_start, block_end = start, end
            else:
                gap: float = (start - block_end).total_seconds()
                if WorkRule.is_block_boundary(gap, start.hour):
                    blocks.append((block_start, block_end))
                    block_start, block_end = start, end
                else:
                    block_end = max(block_end, end)
        if block_start is not None:
            blocks.append((block_start, block_end))
        return blocks
