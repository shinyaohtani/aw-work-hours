"""勤務区間を勤務日ごとにグルーピングしたもの"""

from datetime import date

from .afk_events import AFKEvents
from .work_span import WorkSpan


class WorkEventSpans:
    """not-afkの勤務区間を勤務日ごとにグルーピングしたもの"""

    def __init__(self, events: AFKEvents) -> None:
        self._events: AFKEvents = events

    @property
    def by_day(self) -> dict[date, list[WorkSpan]]:
        grouped: dict[date, list[WorkSpan]] = {}
        for span in self._events.spans:
            grouped.setdefault(span.work_date, []).append(span)
        return grouped
