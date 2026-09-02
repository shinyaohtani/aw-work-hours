"""勤務区間（開始・終了時刻の組）"""

from datetime import date, datetime, timedelta

from ..types import _TIMEZONE, AWEvent, HTMLSpan
from .work_rule import WorkRule


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
        return WorkRule.span_hours(self._start, self._end)

    def merged(self, other: "WorkSpan") -> "WorkSpan":
        return WorkSpan(min(self._start, other._start), max(self._end, other._end))

    def html_dict(self, base: date) -> HTMLSpan:
        return {
            "startH": WorkRule.adjusted_hour(self._start, base),
            "startM": self._start.minute,
            "endH": WorkRule.adjusted_hour(self._end, base),
            "endM": self._end.minute,
        }

    @classmethod
    def list_from_events(cls, events: list[AWEvent]) -> list["WorkSpan"]:
        ordered: list[AWEvent] = sorted(
            (
                e
                for e in events
                if e["data"]["status"] == "not-afk"
                and e["duration"] >= WorkRule.MIN_EVENT_SECONDS
            ),
            key=lambda e: e["timestamp"],
        )
        spans: list[WorkSpan] = []
        for event in ordered:
            start: datetime = datetime.fromisoformat(event["timestamp"]).astimezone(
                _TIMEZONE
            )
            spans.append(cls(start, start + timedelta(seconds=event["duration"])))
        return spans
