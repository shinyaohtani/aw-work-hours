"""日ごとの勤務統計"""

from datetime import date, datetime

from ..types import _TIMEZONE
from .afk_events import AFKEvents
from .day_spans import DaySpans
from .work_event_spans import WorkEventSpans
from .work_moment import WorkMoment
from .work_span import WorkSpan


class DailyWork:
    """日ごとの勤務統計"""

    def __init__(self, events: AFKEvents) -> None:
        self._events: AFKEvents = events

    @property
    def active(self) -> dict[date, float]:
        result: dict[date, float] = {}
        for event in self._events.raw:
            if event["data"]["status"] != "not-afk":
                continue
            start: datetime = datetime.fromisoformat(event["timestamp"]).astimezone(
                _TIMEZONE
            )
            wd: date = WorkMoment(start).work_date
            result[wd] = result.get(wd, 0) + event["duration"]
        return result

    @property
    def gaps(self) -> dict[date, float]:
        by_day: dict[date, list[WorkSpan]] = WorkEventSpans(self._events).by_day
        return {wd: DaySpans(spans).max_gap for wd, spans in by_day.items()}
