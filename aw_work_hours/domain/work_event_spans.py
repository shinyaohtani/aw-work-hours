"""勤務区間を勤務日ごとにグルーピングしたもの"""

from datetime import date

from ..types import AWEvent
from .work_rule import WorkRule
from .work_span import WorkSpan


class WorkEventSpans:
    """not-afkの勤務区間を勤務日ごとにグルーピングしたもの"""

    def __init__(self, events: list[AWEvent]) -> None:
        self._spans: list[WorkSpan] = WorkSpan.list_from_events(events)

    @property
    def by_day(self) -> dict[date, list[WorkSpan]]:
        grouped: dict[date, list[WorkSpan]] = {}
        for span in self._spans:
            wd: date = WorkRule.work_date(span.start)
            grouped.setdefault(wd, []).append(span)
        return grouped
