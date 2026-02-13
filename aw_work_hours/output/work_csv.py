"""CSV出力"""

from datetime import date, datetime

from ..types import _WEEKDAYS
from ..domain.month_period import MonthPeriod
from ..domain.work_rule import WorkRule


class WorkCSV:
    """CSV出力"""

    def __init__(
        self,
        daily: dict[date, tuple[datetime, datetime]],
        active: dict[date, float],
        max_gap: dict[date, float],
        period: MonthPeriod,
    ) -> None:
        self._daily: dict[date, tuple[datetime, datetime]] = daily
        self._active: dict[date, float] = active
        self._max_gap: dict[date, float] = max_gap
        self._period: MonthPeriod = period

    def content(self) -> str:
        lines: list[str] = [
            "date,weekday,start_time,end_time,duration_hours,afk_hours,max_gap_hours"
        ]
        for d in self._date_range():
            lines.append(self._row(d))
        return "\n".join(lines) + "\n"

    def _date_range(self) -> list[date]:
        dates: list[date] = self._period.date_range()
        return dates if dates else sorted(self._daily.keys())

    def _row(self, d: date) -> str:
        prefix: str = f'="{d.strftime("%Y-%m-%d")}",{_WEEKDAYS[d.weekday()]}'
        if d not in self._daily:
            return f"{prefix},,,,,"
        start, end = self._daily[d]
        span: float = WorkRule.span_hours(start, end)
        active: float = self._active.get(d, 0) / 3600
        afk: float = span - active
        max_gap: float = self._max_gap.get(d, 0) / 3600
        return f'{prefix},="{self._time(start, d)}",="{self._time(end, d)}",{span:.2f},{afk:.2f},{max_gap:.2f}'

    def _time(self, dt: datetime, base: date) -> str:
        hour: int = WorkRule.adjusted_hour(dt, base)
        return f"{hour:02d}:{dt.minute:02d}"
