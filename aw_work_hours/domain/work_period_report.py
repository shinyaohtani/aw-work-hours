"""指定期間の勤務集計"""

from .afk_bucket import AFKBucket
from .afk_events import AFKEvents
from .afk_events_request import AFKEventsRequest
from .daily_work import DailyWork
from .month_period import MonthPeriod
from .work_calendar import WorkCalendar


class WorkPeriodReport:
    """指定期間の勤務集計（カレンダー・日次統計・生イベント）"""

    def __init__(
        self, period: MonthPeriod, bucket: AFKBucket, min_event_seconds: int
    ) -> None:
        self._period: MonthPeriod = period
        self._bucket: AFKBucket = bucket
        self._min_event_seconds: int = min_event_seconds
        self._events: AFKEvents | None = None
        self._daily_work: DailyWork | None = None
        self._calendar: WorkCalendar | None = None

    @property
    def period(self) -> MonthPeriod:
        return self._period

    @property
    def events(self) -> AFKEvents:
        if self._events is None:
            self._events = AFKEventsRequest(
                self._bucket, self._period, self._min_event_seconds
            ).events
        events: AFKEvents = self._events
        return events

    @property
    def daily_work(self) -> DailyWork:
        if self._daily_work is None:
            self._daily_work = DailyWork(self.events)
        daily_work: DailyWork = self._daily_work
        return daily_work

    @property
    def calendar(self) -> WorkCalendar:
        if self._calendar is None:
            self._calendar = WorkCalendar(self.events.work_blocks)
        calendar: WorkCalendar = self._calendar
        return calendar
