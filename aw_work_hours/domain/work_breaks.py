"""休憩区間（16分以上の空白）"""

from datetime import date, datetime, timedelta

from ..types import _TIMEZONE, AWEvent
from .work_rule import WorkRule


class WorkBreaks:
    """休憩区間（16分以上の空白）"""

    MIN_SECONDS: int = 16 * 60

    def __init__(self, events: list[AWEvent]) -> None:
        self._not_afk: list[AWEvent] = [
            e
            for e in events
            if e["data"]["status"] == "not-afk"
            and e["duration"] >= WorkRule.MIN_EVENT_SECONDS
        ]

    @property
    def by_day(self) -> dict[date, list[tuple[datetime, datetime]]]:
        result: dict[date, list[tuple[datetime, datetime]]] = {}
        for wd, spans in self._group_by_day().items():
            result[wd] = self._breaks_in_day(spans)
        return result

    def _group_by_day(self) -> dict[date, list[tuple[datetime, datetime]]]:
        grouped: dict[date, list[tuple[datetime, datetime]]] = {}
        for event in self._not_afk:
            start: datetime = datetime.fromisoformat(event["timestamp"]).astimezone(
                _TIMEZONE
            )
            end: datetime = start + timedelta(seconds=event["duration"])
            wd: date = WorkRule.work_date(start)
            grouped.setdefault(wd, []).append((start, end))
        return grouped

    def _breaks_in_day(
        self, spans: list[tuple[datetime, datetime]]
    ) -> list[tuple[datetime, datetime]]:
        sorted_spans: list[tuple[datetime, datetime]] = sorted(spans)
        breaks: list[tuple[datetime, datetime]] = []
        max_end: datetime = sorted_spans[0][1]
        for start, end in sorted_spans[1:]:
            if (start - max_end).total_seconds() >= self.MIN_SECONDS:
                breaks.append((max_end, start))
            max_end = max(max_end, end)
        return breaks
