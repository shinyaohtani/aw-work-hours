"""月の期間"""

from datetime import date, datetime, timedelta

from ..types import _TIMEZONE, CLIError


class MonthPeriod:
    """月の期間"""

    def __init__(self, start: datetime | None, end: datetime | None) -> None:
        self._start: datetime | None = start
        self._end: datetime | None = end

    @classmethod
    def parse(cls, month_str: str) -> "MonthPeriod":
        if month_str == "all":
            return cls(None, None)
        year, month = cls._parse_year_month(month_str)
        start: datetime = datetime(year, month, 1, tzinfo=_TIMEZONE)
        end_year, end_month = (year + 1, 1) if month == 12 else (year, month + 1)
        end: datetime = datetime(end_year, end_month, 1, tzinfo=_TIMEZONE)
        return cls(start, end)

    @classmethod
    def _parse_year_month(cls, month_str: str) -> tuple[int, int]:
        now: datetime = datetime.now(_TIMEZONE)
        if month_str == "this":
            return now.year, now.month
        if month_str == "last":
            return (now.year - 1, 12) if now.month == 1 else (now.year, now.month - 1)
        try:
            year, month = map(int, month_str.split("-"))
            return year, month
        except ValueError:
            raise CLIError(f"エラー: 無効な月指定です: {month_str}")

    @property
    def iso(self) -> tuple[str | None, str | None]:
        return (
            self._start.isoformat() if self._start else None,
            self._end.isoformat() if self._end else None,
        )

    def date_range(self) -> list[date]:
        if not (self._start and self._end):
            return []
        today: date = datetime.now(_TIMEZONE).date()
        result: list[date] = []
        current: date = self._start.date()
        end: date = min(self._end.date(), today + timedelta(days=1))
        while current < end:
            result.append(current)
            current += timedelta(days=1)
        return result
