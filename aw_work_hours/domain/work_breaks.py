"""休憩区間（16分以上の空白）"""

from datetime import date

from .afk_events import AFKEvents
from .day_spans import DaySpans
from .work_event_spans import WorkEventSpans
from .work_span import WorkSpan


class WorkBreaks:
    """休憩区間（16分以上の空白）"""

    def __init__(self, events: AFKEvents, min_seconds: int = 16 * 60) -> None:
        self._events: AFKEvents = events
        self._min_seconds: int = min_seconds

    @property
    def by_day(self) -> dict[date, list[WorkSpan]]:
        by_day: dict[date, list[WorkSpan]] = WorkEventSpans(self._events).by_day
        return {
            wd: DaySpans(spans).breaks(self._min_seconds)
            for wd, spans in by_day.items()
        }
