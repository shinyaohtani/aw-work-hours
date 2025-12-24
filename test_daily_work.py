#!/usr/bin/env python3
"""DailyWorkクラスのテスト"""

import sys
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

_TIMEZONE = ZoneInfo("Asia/Tokyo")


class DailyWork:
    """日ごとの勤務統計 - 修正版"""

    def __init__(self, events: list[dict]) -> None:
        self._not_afk: list[dict] = [
            e for e in events if e["data"]["status"] == "not-afk"
        ]

    @property
    def gaps(self) -> dict[date, float]:
        events_by_day: dict[date, list[tuple[datetime, datetime]]] = {}
        for event in self._not_afk:
            if event["duration"] < 5:
                continue  # 5秒未満のイベント（ノイズ/ミス）を除外
            start: datetime = datetime.fromisoformat(event["timestamp"]).astimezone(
                _TIMEZONE
            )
            end: datetime = start + timedelta(seconds=event["duration"])
            wd: date = self._work_date(start)
            if wd not in events_by_day:
                events_by_day[wd] = []
            events_by_day[wd].append((start, end))
        return self._calc_max_gaps(events_by_day)

    def _calc_max_gaps(
        self, events_by_day: dict[date, list[tuple[datetime, datetime]]]
    ) -> dict[date, float]:
        result: dict[date, float] = {}
        for wd, events in events_by_day.items():
            sorted_events: list[tuple[datetime, datetime]] = sorted(events)
            max_gap: float = 0
            max_end: datetime = sorted_events[0][1] if sorted_events else datetime.min
            for i in range(1, len(sorted_events)):
                gap: float = (sorted_events[i][0] - max_end).total_seconds()
                if gap > 0:
                    max_gap = max(max_gap, gap)
                max_end = max(max_end, sorted_events[i][1])
            result[wd] = max_gap
        return result

    def _work_date(self, dt: datetime) -> date:
        return (dt - timedelta(days=1)).date() if 0 <= dt.hour < 5 else dt.date()


def test_zero_duration_events_should_be_ignored() -> None:
    """0秒イベント（ハートビート）はギャップ計算から除外すべき

    2025-11-27の実データを模倣:
    - 19:00 - 19:13:05 (実アクティビティ)
    - 19:30:01 (0秒イベント) ← 無視すべき
    - 19:45:17 (0秒イベント) ← 無視すべき
    - 20:02:36 (0秒イベント) ← 無視すべき
    - 20:41:52 - 20:49:06 (実アクティビティ)

    正解: 0秒イベントを無視するため、max gap = 20:41:52 - 19:13:05 ≈ 1.5h
    """
    events: list[dict] = [
        {
            "timestamp": "2025-11-27T19:00:00+09:00",
            "duration": 786,  # 13分6秒
            "data": {"status": "not-afk"},
        },
        {
            "timestamp": "2025-11-27T19:30:01+09:00",
            "duration": 0,
            "data": {"status": "not-afk"},
        },
        {
            "timestamp": "2025-11-27T19:45:17+09:00",
            "duration": 0,
            "data": {"status": "not-afk"},
        },
        {
            "timestamp": "2025-11-27T20:02:36+09:00",
            "duration": 0,
            "data": {"status": "not-afk"},
        },
        {
            "timestamp": "2025-11-27T20:41:52+09:00",
            "duration": 434,  # 7分14秒
            "data": {"status": "not-afk"},
        },
    ]

    daily_work = DailyWork(events)
    gaps = daily_work.gaps
    base_date = date(2025, 11, 27)

    actual_gap = gaps.get(base_date, 0) / 3600
    expected_min_gap = 1.4

    print(f"Calculated max gap: {actual_gap:.2f}h")
    print(f"Expected min gap: >= {expected_min_gap}h")

    assert actual_gap >= expected_min_gap, (
        f"Max gap should be at least {expected_min_gap}h, but got {actual_gap:.2f}h. "
        f"Bug: 0-duration events are being counted as activity."
    )
    print("✓ Test passed: zero_duration_events_should_be_ignored")


def test_overlapping_events_use_max_end_time() -> None:
    """重複イベントでは最大終了時刻を使用すべき

    Events:
    - 10:00 - 11:00 (1h)
    - 10:30 - 10:45 (15min) ← 完全に含まれる
    - 12:00 - 13:00 (1h)

    正解: 11:00から計算すると gap = 1h
    """
    events: list[dict] = [
        {
            "timestamp": "2025-11-27T10:00:00+09:00",
            "duration": 3600,
            "data": {"status": "not-afk"},
        },
        {
            "timestamp": "2025-11-27T10:30:00+09:00",
            "duration": 900,
            "data": {"status": "not-afk"},
        },
        {
            "timestamp": "2025-11-27T12:00:00+09:00",
            "duration": 3600,
            "data": {"status": "not-afk"},
        },
    ]

    daily_work = DailyWork(events)
    gaps = daily_work.gaps
    base_date = date(2025, 11, 27)

    actual_gap = gaps.get(base_date, 0) / 3600
    expected_gap = 1.0

    print(f"Calculated max gap: {actual_gap:.2f}h")
    print(f"Expected gap: {expected_gap}h")

    assert abs(actual_gap - expected_gap) < 0.01, (
        f"Max gap should be {expected_gap}h, but got {actual_gap:.2f}h. "
        f"Bug: not tracking max end time for overlapping events."
    )
    print("✓ Test passed: overlapping_events_use_max_end_time")


if __name__ == "__main__":
    print("Running tests...\n")
    failed = False

    try:
        test_zero_duration_events_should_be_ignored()
    except AssertionError as e:
        print(f"✗ FAILED: {e}\n")
        failed = True
    else:
        print()

    try:
        test_overlapping_events_use_max_end_time()
    except AssertionError as e:
        print(f"✗ FAILED: {e}\n")
        failed = True

    if failed:
        print("\n✗ Some tests failed!")
        sys.exit(1)
    else:
        print("\n✓ All tests passed!")
