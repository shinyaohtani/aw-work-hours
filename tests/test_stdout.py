"""stdout出力の回帰テスト

fixtures/ 内のAPIレスポンスを使い、ActivityWatch APIに接続せずに
各月のstdout出力がリファクタリング前と一致することを検証する。
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aw_work_hours.domain import HolidayCalendar, MonthPeriod, WorkCalendar
from aw_work_hours.output import WorkText

_FIXTURES: Path = Path(__file__).parent.parent / "fixtures"
_MONTHS: list[str] = [f"2025-{m:02d}" for m in range(1, 13)] + ["2026-01"]


def _load_fixture(name: str) -> bytes:
    return (_FIXTURES / name).read_bytes()


def _mock_urlopen(month: str):  # type: ignore[no-untyped-def]
    """urllib.request.urlopen の代替: fixtureからレスポンスを返す"""
    buckets_data: bytes = _load_fixture("api/buckets.json")
    events_data: bytes = _load_fixture(f"api/events/{month}.json")
    events_first: bytes = json.dumps(json.loads(events_data)[:1]).encode()

    def side_effect(url: str, **kwargs: object) -> MagicMock:
        resp: MagicMock = MagicMock()
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        if "/events" in url:
            if "limit=1" in url:
                resp.read.return_value = events_first
            else:
                resp.read.return_value = events_data
        elif "/buckets" in url:
            resp.read.return_value = buckets_data
        else:
            raise ValueError(f"Unexpected URL in test: {url}")
        resp.read.return_value = resp.read.return_value
        return resp

    return side_effect


@pytest.mark.parametrize("month", _MONTHS)
def test_stdout(month: str) -> None:
    """リファクタリング後のstdout出力がfixture期待値と一致する"""
    expected: str = (_FIXTURES / "expected" / f"{month}.txt").read_text()

    with patch(
        "aw_work_hours.domain.urllib.request.urlopen",
        side_effect=_mock_urlopen(month),
    ):
        period = MonthPeriod.parse(month)
        calendar, daily_work, _events = WorkCalendar.from_period(period)
        holidays = HolidayCalendar()
        holidays._cache_dir = _FIXTURES / "holidays"
        text = WorkText(
            calendar.daily,
            daily_work.active,
            daily_work.gaps,
            period,
            holidays,
        )
        actual: str = text.content()

    assert actual == expected, (
        f"stdout mismatch for {month}:\n"
        f"--- expected ---\n{expected}\n"
        f"--- actual ---\n{actual}"
    )
