"""勤務カレンダー"""

from datetime import date

from .work_span import WorkSpan


class WorkCalendar:
    """勤務カレンダー"""

    def __init__(self, blocks: list[WorkSpan]) -> None:
        self._blocks: list[WorkSpan] = blocks
        self._daily: dict[date, WorkSpan] = self._merge_by_day()

    def _merge_by_day(self) -> dict[date, WorkSpan]:
        daily: dict[date, WorkSpan] = {}
        for block in self._blocks:
            wd: date = block.work_date
            daily[wd] = block if wd not in daily else daily[wd].merged(block)
        return daily

    @property
    def days(self) -> int:
        return len(self._daily)

    @property
    def daily(self) -> dict[date, WorkSpan]:
        return self._daily
