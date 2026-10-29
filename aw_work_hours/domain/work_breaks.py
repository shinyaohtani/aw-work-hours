"""休憩区間"""

from datetime import date

from .afk_events import AFKEvents
from .break_rule import BreakRule
from .day_spans import DaySpans
from .work_event_spans import WorkEventSpans
from .work_span import WorkSpan


class WorkBreaks:
    """休憩区間（BreakRuleの基準を満たす空白）"""

    def __init__(self, events: AFKEvents, rule: BreakRule) -> None:
        self._events: AFKEvents = events
        self._rule: BreakRule = rule

    @property
    def by_day(self) -> dict[date, list[WorkSpan]]:
        by_day: dict[date, list[WorkSpan]] = WorkEventSpans(self._events).by_day
        return {wd: DaySpans(spans).breaks(self._rule) for wd, spans in by_day.items()}
