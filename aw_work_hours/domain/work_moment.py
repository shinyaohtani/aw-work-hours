"""勤務ドメインの時刻"""

from datetime import date, datetime, timedelta


class WorkMoment:
    """勤務ドメインの時刻（日境界などのルールを内包する1つの時刻）"""

    _DAY_BOUNDARY_HOUR: int = 5

    def __init__(self, moment: datetime) -> None:
        self._moment: datetime = moment

    @property
    def work_date(self) -> date:
        """勤務日: 0:00-4:59は前日扱い"""
        if 0 <= self._moment.hour < self._DAY_BOUNDARY_HOUR:
            return (self._moment - timedelta(days=1)).date()
        return self._moment.date()

    def adjusted_hour(self, base: date) -> int:
        """日跨ぎ対応の時間表示（25:00等）"""
        return self._moment.hour + ((self._moment.date() - base).days * 24)

    def hhmm(self, base: date, colon: bool = True) -> str:
        sep: str = ":" if colon else ""
        return f"{self.adjusted_hour(base):02d}{sep}{self._moment.minute:02d}"
