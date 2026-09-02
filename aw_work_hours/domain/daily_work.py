"""日ごとの勤務統計"""

from datetime import date, datetime

from ..types import _TIMEZONE, AWEvent
from .work_event_spans import WorkEventSpans
from .work_rule import WorkRule
from .work_span import WorkSpan


class DailyWork:
    """日ごとの勤務統計"""

    def __init__(self, events: list[AWEvent]) -> None:
        self._not_afk: list[AWEvent] = [
            e for e in events if e["data"]["status"] == "not-afk"
        ]
        self._spans_by_day: dict[date, list[WorkSpan]] = WorkEventSpans(events).by_day

    @property
    def active(self) -> dict[date, float]:
        result: dict[date, float] = {}
        for event in self._not_afk:
            start: datetime = datetime.fromisoformat(event["timestamp"]).astimezone(
                _TIMEZONE
            )
            wd: date = WorkRule.work_date(start)
            result[wd] = result.get(wd, 0) + event["duration"]
        return result

    @property
    def gaps(self) -> dict[date, float]:
        return {wd: self._max_gap(spans) for wd, spans in self._spans_by_day.items()}

    def _max_gap(self, spans: list[WorkSpan]) -> float:
        ordered: list[WorkSpan] = sorted(spans, key=lambda s: s.start)
        max_gap: float = 0
        max_end: datetime = ordered[0].end
        for span in ordered[1:]:
            gap: float = (span.start - max_end).total_seconds()
            if gap > 0:
                max_gap = max(max_gap, gap)
            max_end = max(max_end, span.end)
        return max_gap
