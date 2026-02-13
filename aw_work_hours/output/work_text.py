"""テキスト出力"""

from datetime import date, datetime, timedelta

from ..types import _WEEKDAYS
from ..domain.holiday_calendar import HolidayCalendar
from ..domain.month_period import MonthPeriod
from ..domain.work_rule import WorkRule


class WorkText:
    """テキスト出力"""

    def __init__(
        self,
        daily: dict[date, tuple[datetime, datetime]],
        active: dict[date, float],
        max_gap: dict[date, float],
        period: MonthPeriod,
        holidays: HolidayCalendar,
        no_colon: bool = False,
    ) -> None:
        self._daily: dict[date, tuple[datetime, datetime]] = daily
        self._active: dict[date, float] = active
        self._max_gap: dict[date, float] = max_gap
        self._period: MonthPeriod = period
        self._holidays: HolidayCalendar = holidays
        self._no_colon: bool = no_colon

    def content(self) -> str:
        dates: list[date] = self._period.date_range()
        if not dates and self._daily:
            start: date = min(self._daily.keys())
            end: date = max(self._daily.keys()) + timedelta(days=1)
            current: date = start
            while current < end:
                dates.append(current)
                current += timedelta(days=1)
        lines: list[str] = [self._day(d) for d in dates]
        return "\n".join(lines) + "\n" if lines else ""

    def _day(self, d: date) -> str:
        weekday: str = _WEEKDAYS[d.weekday()]
        has_work: bool = d in self._daily
        is_holiday: bool = has_work and self._holidays.is_holiday(d)
        holiday_mark: str = "*" if is_holiday else ""
        prefix: str = f'{d.strftime("%Y-%m-%d")} {weekday}{holiday_mark}'
        if not has_work:
            return prefix
        return self._format_work_day(d, prefix, is_holiday)

    def _format_work_day(self, d: date, prefix: str, is_holiday: bool) -> str:
        s, e = self._daily[d]
        span: float = WorkRule.span_hours(s, e)
        if round(span, 1) == 0:
            return prefix
        active: float = self._active.get(d, 0) / 3600
        afk: float = span - active
        spacing: str = "  " if is_holiday else "   "
        base: str = (
            f"{prefix}{spacing}{self._time(s, d)} - {self._time(e, d)}   ({span:.1f}h)"
        )
        if afk < 0.05:
            return base
        max_gap: float = self._max_gap.get(d, 0) / 3600
        return f"{base}   -{afk:.1f}h (max:-{max_gap:.1f}h)"

    def _time(self, dt: datetime, base: date) -> str:
        hour: int = WorkRule.adjusted_hour(dt, base)
        sep: str = "" if self._no_colon else ":"
        return f"{hour:02d}{sep}{dt.minute:02d}"
