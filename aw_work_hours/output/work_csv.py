"""CSV出力"""

from datetime import date

from ..types import _WEEKDAYS
from ..domain.work_moment import WorkMoment
from ..domain.work_period_report import WorkPeriodReport
from ..domain.work_span import WorkSpan


class WorkCSV:
    """CSV出力"""

    def __init__(self, report: WorkPeriodReport) -> None:
        self._report: WorkPeriodReport = report

    def content(self) -> str:
        lines: list[str] = [
            "date,weekday,start_time,end_time,duration_hours,afk_hours,max_gap_hours"
        ]
        for d in self._date_range():
            lines.append(self._row(d))
        return "\n".join(lines) + "\n"

    def _date_range(self) -> list[date]:
        dates: list[date] = self._report.period.date_range()
        return dates if dates else sorted(self._report.calendar.daily.keys())

    def _row(self, d: date) -> str:
        prefix: str = f'="{d.strftime("%Y-%m-%d")}",{_WEEKDAYS[d.weekday()]}'
        daily: dict[date, WorkSpan] = self._report.calendar.daily
        if d not in daily:
            return f"{prefix},,,,,"
        span: WorkSpan = daily[d]
        active: float = self._report.daily_work.active.get(d, 0) / 3600
        afk: float = span.hours - active
        max_gap: float = self._report.daily_work.gaps.get(d, 0) / 3600
        start_label: str = WorkMoment(span.start).hhmm(d)
        end_label: str = WorkMoment(span.end).hhmm(d)
        return (
            f'{prefix},="{start_label}",="{end_label}",'
            f"{span.hours:.2f},{afk:.2f},{max_gap:.2f}"
        )
