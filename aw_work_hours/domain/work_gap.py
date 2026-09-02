"""2つの勤務区間の間の空白"""

from datetime import datetime


class WorkGap:
    """2つの勤務区間の間の空白（前の終了時刻と次の開始時刻の組）"""

    _BLOCK_SECONDS: int = 3 * 60 * 60
    _DAY_BOUNDARY_HOUR: int = 5

    def __init__(self, previous_end: datetime, next_start: datetime) -> None:
        self._previous_end: datetime = previous_end
        self._next_start: datetime = next_start

    @property
    def seconds(self) -> float:
        return (self._next_start - self._previous_end).total_seconds()

    @property
    def is_block_boundary(self) -> bool:
        """3時間超の離席 かつ 5:00以降に再開 → 新ブロック"""
        return (
            self.seconds > self._BLOCK_SECONDS
            and self._next_start.hour >= self._DAY_BOUNDARY_HOUR
        )
