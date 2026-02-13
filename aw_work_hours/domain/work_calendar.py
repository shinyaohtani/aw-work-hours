"""勤務カレンダー"""

from datetime import date, datetime

from .afk_events import AFKEvents
from .daily_work import DailyWork
from .month_period import MonthPeriod
from .work_rule import WorkRule


class WorkCalendar:
    """勤務カレンダー"""

    def __init__(self, daily: dict[date, tuple[datetime, datetime]]) -> None:
        self._daily: dict[date, tuple[datetime, datetime]] = daily

    @classmethod
    def from_blocks(cls, blocks: list[tuple[datetime, datetime]]) -> "WorkCalendar":
        daily: dict[date, tuple[datetime, datetime]] = {}
        for block_start, block_end in blocks:
            wd: date = WorkRule.work_date(block_start)
            if wd not in daily:
                daily[wd] = (block_start, block_end)
            else:
                s, e = daily[wd]
                daily[wd] = (min(block_start, s), max(block_end, e))
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
    def daily(self) -> dict[date, tuple[datetime, datetime]]:
        return self._daily
