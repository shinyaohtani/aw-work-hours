"""HTML APIレスポンス生成"""

from datetime import datetime, timedelta

from ..types import _TIMEZONE, AWEvent
from ..domain import (
    AFKEvents,
    DailyWork,
    HolidayCalendar,
    MonthPeriod,
    WorkCalendar,
    WorkRule,
)
from .work_html_row import WorkHTMLRow


class WorkHTMLResponse:
    """HTML APIレスポンス生成"""

    def __init__(self, period: MonthPeriod) -> None:
        self._period: MonthPeriod = period

    def json(self) -> dict:
        calendar, daily_work, events = WorkCalendar.from_period(self._period)
        holidays: HolidayCalendar = HolidayCalendar()
        rows: list[WorkHTMLRow] = self._create_rows(calendar, daily_work, holidays)
        self._populate_events(rows, events)
        return {"rows": [r.to_dict() for r in rows]}

    def _create_rows(
        self, calendar: WorkCalendar, daily_work: DailyWork, holidays: HolidayCalendar
    ) -> list[WorkHTMLRow]:
        return [
            WorkHTMLRow(d, calendar, daily_work, holidays)
            for d in self._period.date_range()
        ]

    def _populate_events(self, rows: list[WorkHTMLRow], events: AFKEvents) -> None:
        not_afk: list[AWEvent] = [
            e
            for e in events.raw
            if e["data"]["status"] == "not-afk"
            and e["duration"] >= WorkRule.MIN_EVENT_SECONDS
        ]
        for ev in not_afk:
            start: datetime = datetime.fromisoformat(ev["timestamp"]).astimezone(
                _TIMEZONE
            )
            end: datetime = start + timedelta(seconds=ev["duration"])
            for row in rows:
                row.add_event(start, end, ev)
