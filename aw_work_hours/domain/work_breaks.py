"""休憩区間（16分以上の空白）"""

from datetime import date, datetime

from ..types import AWEvent
from .work_event_spans import WorkEventSpans
from .work_span import WorkSpan


class WorkBreaks:
    """休憩区間（16分以上の空白）"""

    MIN_SECONDS: int = 16 * 60

    def __init__(self, events: list[AWEvent]) -> None:
        self._spans_by_day: dict[date, list[WorkSpan]] = WorkEventSpans(events).by_day

    @property
    def by_day(self) -> dict[date, list[WorkSpan]]:
        return {
            wd: self._breaks_in_day(spans) for wd, spans in self._spans_by_day.items()
        }

    def _breaks_in_day(self, spans: list[WorkSpan]) -> list[WorkSpan]:
        ordered: list[WorkSpan] = sorted(spans, key=lambda s: s.start)
        breaks: list[WorkSpan] = []
        max_end: datetime = ordered[0].end
        for span in ordered[1:]:
            if (span.start - max_end).total_seconds() >= self.MIN_SECONDS:
                breaks.append(WorkSpan(max_end, span.start))
            max_end = max(max_end, span.end)
        return breaks
