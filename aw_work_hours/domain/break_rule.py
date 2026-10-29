"""休憩とみなす空白の基準"""

from datetime import datetime, time

from .work_span import WorkSpan


class BreakRule:
    """休憩とみなす空白の基準（コア時間帯は最短時間を長くとる）"""

    def __init__(
        self, minutes: int = 15, core_minutes: int = 30, core_hours: str = "09:00-18:00"
    ) -> None:
        self._minutes: int = minutes
        self._core_minutes: int = core_minutes
        self._core_hours: str = core_hours
        start_label, end_label = core_hours.split("-")
        self._core_start: time = time.fromisoformat(start_label.strip())
        self._core_end: time = time.fromisoformat(end_label.strip())

    def includes(self, gap: WorkSpan) -> bool:
        seconds: float = (gap.end - gap.start).total_seconds()
        return seconds >= self._threshold_minutes(gap.start) * 60

    @property
    def as_dict(self) -> dict[str, object]:
        return {
            "break_minutes": self._minutes,
            "core_break_minutes": self._core_minutes,
            "core_hours": self._core_hours,
        }

    def _threshold_minutes(self, start: datetime) -> int:
        in_core: bool = self._core_start <= start.time() < self._core_end
        return self._core_minutes if in_core else self._minutes
