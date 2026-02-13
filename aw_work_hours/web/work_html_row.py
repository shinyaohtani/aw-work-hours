"""HTML用の日別行データ"""

from datetime import date, datetime, timedelta

from ..types import _WEEKDAYS, _TIMEZONE, AWEvent, HTMLEvent
from ..domain import DailyWork, HolidayCalendar, WorkCalendar, WorkRule


class WorkHTMLRow:
    """HTML用の日別行データ"""

    def __init__(
        self,
        d: date,
        calendar: WorkCalendar,
        daily_work: DailyWork,
        holidays: HolidayCalendar,
    ) -> None:
        self._date: date = d
        self._calendar: WorkCalendar = calendar
        self._daily_work: DailyWork = daily_work
        self._holidays: HolidayCalendar = holidays
        self._events: list[HTMLEvent] = []

    def add_event(self, start: datetime, end: datetime, event: AWEvent) -> None:
        current: date = start.date()
        while current <= end.date():
            if current == self._date:
                day_start: datetime = max(
                    start,
                    datetime.combine(current, datetime.min.time()).replace(
                        tzinfo=_TIMEZONE
                    ),
                )
                day_end_limit: datetime = datetime.combine(
                    current + timedelta(days=1), datetime.min.time()
                ).replace(tzinfo=_TIMEZONE)
                day_end: datetime = min(end, day_end_limit)
                if day_end > day_start:
                    self._events.append(
                        self._event_dict(day_start, day_end, current, event)
                    )
            current += timedelta(days=1)

    def _event_dict(
        self, start: datetime, end: datetime, current: date, event: AWEvent
    ) -> HTMLEvent:
        return {
            "startH": start.hour,
            "startM": start.minute,
            "startS": start.second,
            "endH": end.hour if end.date() == current else 24,
            "endM": end.minute if end.date() == current else 0,
            "endS": end.second if end.date() == current else 0,
            "duration": (end - start).total_seconds(),
            "data": event["data"],
        }

    def to_dict(self) -> dict:
        d: date = self._date
        has_work: bool = d in self._calendar.daily
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
        s, e = self._calendar.daily[d]
        span: float = WorkRule.span_hours(s, e)
        row["startH"] = WorkRule.adjusted_hour(s, d)
        row["startM"] = s.minute
        row["endH"] = WorkRule.adjusted_hour(e, d)
        row["endM"] = e.minute
        row["span"] = round(span, 1)
        active_h: float = self._daily_work.active.get(d, 0) / 3600
        afk: float = span - active_h
        if afk >= 0.05:
            row["afk"] = round(afk, 1)
            row["maxGap"] = round(self._daily_work.gaps.get(d, 0) / 3600, 1)
