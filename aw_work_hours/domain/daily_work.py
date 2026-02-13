"""日ごとの勤務統計"""

from datetime import date, datetime, timedelta

from ..types import _TIMEZONE, AWEvent
from .work_rule import WorkRule


class DailyWork:
    """日ごとの勤務統計"""

    def __init__(self, events: list[AWEvent]) -> None:
        self._not_afk: list[AWEvent] = [
            e for e in events if e["data"]["status"] == "not-afk"
        ]

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
        events_by_day: dict[date, list[tuple[datetime, datetime]]] = {}
        for event in self._not_afk:
            if event["duration"] < WorkRule.MIN_EVENT_SECONDS:
                continue
            start: datetime = datetime.fromisoformat(event["timestamp"]).astimezone(
                _TIMEZONE
            )
            end: datetime = start + timedelta(seconds=event["duration"])
            wd: date = WorkRule.work_date(start)
            if wd not in events_by_day:
                events_by_day[wd] = []
            events_by_day[wd].append((start, end))
        return self._calc_max_gaps(events_by_day)

    def _calc_max_gaps(
        self, events_by_day: dict[date, list[tuple[datetime, datetime]]]
    ) -> dict[date, float]:
        result: dict[date, float] = {}
        for wd, events in events_by_day.items():
            sorted_events: list[tuple[datetime, datetime]] = sorted(events)
            max_gap: float = 0
            max_end: datetime = sorted_events[0][1] if sorted_events else datetime.min
            for i in range(1, len(sorted_events)):
                gap: float = (sorted_events[i][0] - max_end).total_seconds()
                if gap > 0:
                    max_gap = max(max_gap, gap)
                max_end = max(max_end, sorted_events[i][1])
            result[wd] = max_gap
        return result
