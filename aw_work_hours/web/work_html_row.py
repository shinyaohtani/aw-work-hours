"""HTML用の日別行データ"""

from datetime import date, datetime, timedelta

from ..types import _WEEKDAYS, _TIMEZONE, AWEvent, HTMLEvent
from ..domain.holiday_calendar import HolidayCalendar
from ..domain.work_period_report import WorkPeriodReport
from ..domain.work_span import WorkSpan


class WorkHTMLRow:
    """HTML用の日別行データ"""

    def __init__(
        self,
        d: date,
        report: WorkPeriodReport,
        holidays: HolidayCalendar,
        breaks: list[WorkSpan] | None = None,
    ) -> None:
        self._date: date = d
        self._report: WorkPeriodReport = report
        self._holidays: HolidayCalendar = holidays
        self._breaks: list[WorkSpan] = breaks or []
        self._events: list[HTMLEvent] = []

    def add_event(self, start: datetime, end: datetime, event: AWEvent) -> None:
        current: date = start.date()
        while current <= end.date():
            if current == self._date:
                self._add_event_on(current, start, end, event)
            current += timedelta(days=1)

    def _add_event_on(
        self, current: date, start: datetime, end: datetime, event: AWEvent
    ) -> None:
        day_start: datetime = max(
            start,
            datetime.combine(current, datetime.min.time()).replace(tzinfo=_TIMEZONE),
        )
        day_end_limit: datetime = datetime.combine(
            current + timedelta(days=1), datetime.min.time()
        ).replace(tzinfo=_TIMEZONE)
        day_end: datetime = min(end, day_end_limit)
        if day_end > day_start:
            self._events.append(
                {
                    "startH": day_start.hour,
                    "startM": day_start.minute,
                    "startS": day_start.second,
                    "endH": day_end.hour if day_end.date() == current else 24,
                    "endM": day_end.minute if day_end.date() == current else 0,
                    "endS": day_end.second if day_end.date() == current else 0,
                    "duration": (day_end - day_start).total_seconds(),
                    "data": event["data"],
                }
            )

    def to_dict(self) -> dict:
        d: date = self._date
        has_work: bool = d in self._report.calendar.daily
        is_holiday: bool = has_work and self._holidays.is_holiday(d)
        row: dict = {
            "date": d.isoformat(),
            "weekday": _WEEKDAYS[d.weekday()],
            "holiday": is_holiday,
            "hasWork": has_work,
        }
        if has_work:
            self._add_work_fields(row, d)
        row["events"] = self._events
        return row

    def _add_work_fields(self, row: dict, d: date) -> None:
        span: WorkSpan = self._report.calendar.daily[d]
        row.update(span.html_dict(d))
        row["span"] = round(span.hours, 1)
        active_h: float = self._report.daily_work.active.get(d, 0) / 3600
        afk: float = span.hours - active_h
        if afk >= 0.05:
            row["afk"] = round(afk, 1)
            row["maxGap"] = round(self._report.daily_work.gaps.get(d, 0) / 3600, 1)
        row["breaks"] = [b.html_dict(d) for b in self._breaks]
