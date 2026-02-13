"""勤務日の判定ルール"""

from datetime import date, datetime, timedelta


class WorkRule:
    """勤務日の判定ルール

    - 0:00-4:59の勤務は前日扱い（日境界 = 5:00）
    - 3時間超の離席 かつ 5:00以降に再開 → 別ブロック
    - 24:00超えは26:00のように表記
    """

    _GAP_SECONDS: int = 3 * 60 * 60
    _DAY_BOUNDARY_HOUR: int = 5
    MIN_EVENT_SECONDS: int = 150

    @staticmethod
    def work_date(dt: datetime) -> date:
        """勤務日: 0:00-4:59は前日扱い"""
        return (dt - timedelta(days=1)).date() if 0 <= dt.hour < 5 else dt.date()

    @staticmethod
    def is_block_boundary(gap_seconds: float, start_hour: int) -> bool:
        """3時間超の離席 かつ 5:00以降に再開 → 新ブロック"""
        return (
            gap_seconds > WorkRule._GAP_SECONDS
            and start_hour >= WorkRule._DAY_BOUNDARY_HOUR
        )

    @staticmethod
    def adjusted_hour(dt: datetime, base: date) -> int:
        """日跨ぎ対応の時間表示（25:00等）"""
        return dt.hour + ((dt.date() - base).days * 24)

    @staticmethod
    def span_hours(start: datetime, end: datetime) -> float:
        """時間幅（時間単位）"""
        return (end - start).total_seconds() / 3600
