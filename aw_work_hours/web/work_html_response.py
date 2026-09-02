"""HTML APIレスポンス生成"""

from datetime import date, datetime, timedelta

from ..types import _TIMEZONE, AWEvent
from ..domain.afk_bucket import AFKBucket
from ..domain.holiday_calendar import HolidayCalendar
from ..domain.month_period import MonthPeriod
from ..domain.work_breaks import WorkBreaks
from ..domain.work_period_report import WorkPeriodReport
from ..domain.work_span import WorkSpan
from .work_html_row import WorkHTMLRow


class WorkHTMLResponse:
    """HTML APIレスポンス生成"""

    def __init__(
        self, period: MonthPeriod, bucket: AFKBucket, min_event_seconds: int
    ) -> None:
        self._period: MonthPeriod = period
        self._bucket: AFKBucket = bucket
        self._min_event_seconds: int = min_event_seconds

    def json(self) -> dict:
        report: WorkPeriodReport = WorkPeriodReport(
            self._period, self._bucket, self._min_event_seconds
        )
        holidays: HolidayCalendar = HolidayCalendar()
        breaks: dict[date, list[WorkSpan]] = WorkBreaks(report.events).by_day
        rows: list[WorkHTMLRow] = self._create_rows(report, holidays, breaks)
        self._populate_events(rows, report)
        return {"rows": [r.to_dict() for r in rows]}

    def _create_rows(
        self,
        report: WorkPeriodReport,
        holidays: HolidayCalendar,
        breaks: dict[date, list[WorkSpan]],
    ) -> list[WorkHTMLRow]:
        return [
            WorkHTMLRow(d, report, holidays, breaks.get(d, []))
            for d in self._period.date_range()
        ]

    def _populate_events(
        self, rows: list[WorkHTMLRow], report: WorkPeriodReport
    ) -> None:
        not_afk: list[AWEvent] = [
            e
            for e in report.events.raw
            if e["data"]["status"] == "not-afk"
            and e["duration"] >= self._min_event_seconds
        ]
        for ev in not_afk:
            start: datetime = datetime.fromisoformat(ev["timestamp"]).astimezone(
                _TIMEZONE
            )
            end: datetime = start + timedelta(seconds=ev["duration"])
            for row in rows:
                row.add_event(start, end, ev)
