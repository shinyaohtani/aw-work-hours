"""1日分の勤務区間の集合"""

from datetime import datetime

from .work_gap import WorkGap
from .work_span import WorkSpan


class DaySpans:
    """1日分の勤務区間の集合"""

    def __init__(self, spans: list[WorkSpan]) -> None:
        self._spans: list[WorkSpan] = sorted(spans, key=lambda s: s.start)

    @property
    def max_gap(self) -> float:
        max_gap: float = 0
        max_end: datetime = self._spans[0].end
        for span in self._spans[1:]:
            gap: float = WorkGap(max_end, span.start).seconds
            if gap > 0:
                max_gap = max(max_gap, gap)
            max_end = max(max_end, span.end)
        return max_gap

    def breaks(self, min_seconds: int) -> list[WorkSpan]:
        breaks: list[WorkSpan] = []
        max_end: datetime = self._spans[0].end
        for span in self._spans[1:]:
            if WorkGap(max_end, span.start).seconds >= min_seconds:
                breaks.append(WorkSpan(max_end, span.start))
            max_end = max(max_end, span.end)
        return breaks
