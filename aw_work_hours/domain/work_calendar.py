"""勤務カレンダー"""

from datetime import date

from .afk_events import AFKEvents
from .daily_work import DailyWork
from .month_period import MonthPeriod
from .work_rule import WorkRule
from .work_span import WorkSpan


class WorkCalendar:
    """勤務カレンダー"""

    def __init__(self, daily: dict[date, WorkSpan]) -> None:
        self._daily: dict[date, WorkSpan] = daily

    @classmethod
    def from_blocks(cls, blocks: list[WorkSpan]) -> "WorkCalendar":
        daily: dict[date, WorkSpan] = {}
        for block in blocks:
            wd: date = WorkRule.work_date(block.start)
            daily[wd] = block if wd not in daily else daily[wd].merged(block)
        return cls(daily)

    @classmethod
    def from_period(
        cls, period: MonthPeriod
    ) -> tuple["WorkCalendar", DailyWork, AFKEvents]:
        """ドメイン計算の入口: 期間→カレンダー・勤務統計・イベント"""
        events: AFKEvents = AFKEvents.fetch(*period.iso)
        daily_work: DailyWork = DailyWork(events.raw)
        calendar: "WorkCalendar" = cls.from_blocks(events.work_blocks)
        return calendar, daily_work, events

    @property
    def days(self) -> int:
        return len(self._daily)

    @property
    def daily(self) -> dict[date, WorkSpan]:
        return self._daily
