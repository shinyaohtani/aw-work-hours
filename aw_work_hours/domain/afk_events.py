"""ActivityWatchのAFKイベント"""

import json
import urllib.error
import urllib.parse
import urllib.request

from ..types import _API_BASE, APIConnectionError, AWEvent
from .afk_bucket import AFKBucket
from .work_rule import WorkRule
from .work_span import WorkSpan


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
    def work_blocks(self) -> list[WorkSpan]:
        spans: list[WorkSpan] = WorkSpan.list_from_events(self._events)
        return self._extract_blocks(spans) if spans else []

    def _extract_blocks(self, spans: list[WorkSpan]) -> list[WorkSpan]:
        blocks: list[WorkSpan] = []
        current: WorkSpan | None = None
        for span in spans:
            if current is None:
                current = span
            elif WorkRule.is_block_boundary(
                (span.start - current.end).total_seconds(), span.start.hour
            ):
                blocks.append(current)
                current = span
            else:
                current = current.merged(span)
        if current is not None:
            blocks.append(current)
        return blocks
