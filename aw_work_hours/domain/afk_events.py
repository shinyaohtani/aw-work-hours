"""ActivityWatchのAFKイベント"""

from datetime import datetime, timedelta

from ..types import _TIMEZONE, AWEvent
from .work_gap import WorkGap
from .work_span import WorkSpan


class AFKEvents:
    """ActivityWatchのAFKイベント"""

    def __init__(self, events: list[AWEvent], min_event_seconds: int) -> None:
        self._events: list[AWEvent] = events
        self._min_event_seconds: int = min_event_seconds
        self._spans: list[WorkSpan] | None = None

    @property
    def raw(self) -> list[AWEvent]:
        return self._events

    @property
    def spans(self) -> list[WorkSpan]:
        """not-afkかつ閾値以上の区間（開始時刻順）"""
        if self._spans is None:
            ordered: list[AWEvent] = sorted(
                (
                    e
                    for e in self._events
                    if e["data"]["status"] == "not-afk"
                    and e["duration"] >= self._min_event_seconds
                ),
                key=lambda e: e["timestamp"],
            )
            spans: list[WorkSpan] = []
            for event in ordered:
                start: datetime = datetime.fromisoformat(
                    event["timestamp"]
                ).astimezone(_TIMEZONE)
                spans.append(WorkSpan(start, start + timedelta(seconds=event["duration"])))
            self._spans = spans
        return self._spans

    @property
    def work_blocks(self) -> list[WorkSpan]:
        return self._extract_blocks() if self.spans else []

    def _extract_blocks(self) -> list[WorkSpan]:
        blocks: list[WorkSpan] = []
        current: WorkSpan | None = None
        for span in self.spans:
            if current is None:
                current = span
            elif WorkGap(current.end, span.start).is_block_boundary:
                blocks.append(current)
                current = span
            else:
                current = current.merged(span)
        if current is not None:
            blocks.append(current)
        return blocks
