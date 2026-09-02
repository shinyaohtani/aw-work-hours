"""勤務区間（開始・終了時刻の組）"""

from datetime import date, datetime

from ..types import HTMLSpan
from .work_moment import WorkMoment


class WorkSpan:
    """勤務区間（開始・終了時刻の組）"""

    def __init__(self, start: datetime, end: datetime) -> None:
        self._start: datetime = start
        self._end: datetime = end

    @property
    def start(self) -> datetime:
        return self._start

    @property
    def end(self) -> datetime:
        return self._end

    @property
    def hours(self) -> float:
        return (self._end - self._start).total_seconds() / 3600

    @property
    def work_date(self) -> date:
        return WorkMoment(self._start).work_date

    def merged(self, other: "WorkSpan") -> "WorkSpan":
        return WorkSpan(min(self._start, other._start), max(self._end, other._end))

    def html_dict(self, base: date) -> HTMLSpan:
        return {
            "startH": WorkMoment(self._start).adjusted_hour(base),
            "startM": self._start.minute,
            "endH": WorkMoment(self._end).adjusted_hour(base),
            "endM": self._end.minute,
        }
