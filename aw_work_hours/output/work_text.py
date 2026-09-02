"""テキスト出力"""

from datetime import date, timedelta

from ..types import _WEEKDAYS
from ..domain.holiday_calendar import HolidayCalendar
from ..domain.work_moment import WorkMoment
from ..domain.work_period_report import WorkPeriodReport
from ..domain.work_span import WorkSpan


class WorkText:
    """テキスト出力"""

    def __init__(
        self,
        report: WorkPeriodReport,
        holidays: HolidayCalendar,
        no_colon: bool = False,
    ) -> None:
        self._report: WorkPeriodReport = report
        self._holidays: HolidayCalendar = holidays
        self._no_colon: bool = no_colon

    def content(self) -> str:
        dates: list[date] = self._report.period.date_range()
        daily: dict[date, WorkSpan] = self._report.calendar.daily
        if not dates and daily:
            start: date = min(daily.keys())
            end: date = max(daily.keys()) + timedelta(days=1)
            current: date = start
            while current < end:
                dates.append(current)
                current += timedelta(days=1)
        lines: list[str] = [self._day(d) for d in dates]
        return "\n".join(lines) + "\n" if lines else ""

    def _day(self, d: date) -> str:
        weekday: str = _WEEKDAYS[d.weekday()]
        has_work: bool = d in self._report.calendar.daily
        is_holiday: bool = has_work and self._holidays.is_holiday(d)
        holiday_mark: str = "*" if is_holiday else ""
        prefix: str = f'{d.strftime("%Y-%m-%d")} {weekday}{holiday_mark}'
        if not has_work:
            return prefix
        return self._format_work_day(d, prefix, is_holiday)

    def _format_work_day(self, d: date, prefix: str, is_holiday: bool) -> str:
        span: WorkSpan = self._report.calendar.daily[d]
        active: float = self._report.daily_work.active.get(d, 0) / 3600
        afk: float = span.hours - active
        spacing: str = "  " if is_holiday else "   "
        start_label: str = WorkMoment(span.start).hhmm(d, colon=not self._no_colon)
        end_label: str = WorkMoment(span.end).hhmm(d, colon=not self._no_colon)
        base: str = f"{prefix}{spacing}{start_label} - {end_label}   ({span.hours:.1f}h)"
        if afk < 0.05:
            return base
        max_gap: float = self._report.daily_work.gaps.get(d, 0) / 3600
        return f"{base}   -{afk:.1f}h (max:-{max_gap:.1f}h)"
