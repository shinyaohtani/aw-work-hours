"""ActivityWatchへのAFKイベント取得リクエスト"""

import json
import urllib.error
import urllib.parse
import urllib.request

from ..types import _API_BASE, APIConnectionError
from .afk_bucket import AFKBucket
from .afk_events import AFKEvents
from .month_period import MonthPeriod


class AFKEventsRequest:
    """ActivityWatchへのAFKイベント取得リクエスト"""

    def __init__(
        self, bucket: AFKBucket, period: MonthPeriod, min_event_seconds: int
    ) -> None:
        self._bucket: AFKBucket = bucket
        self._period: MonthPeriod = period
        self._min_event_seconds: int = min_event_seconds

    @property
    def url(self) -> str:
        start, end = self._period.iso
        params: dict[str, str] = {"limit": "-1"}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return f"{_API_BASE}/buckets/{self._bucket.id}/events?" + urllib.parse.urlencode(
            params
        )

    @property
    def events(self) -> AFKEvents:
        try:
            with urllib.request.urlopen(self.url, timeout=30) as resp:
                return AFKEvents(
                    json.loads(resp.read().decode()), self._min_event_seconds
                )
        except urllib.error.URLError as e:
            raise APIConnectionError(
                "エラー: ActivityWatch APIに接続できません\n"
                "ActivityWatchが起動しているか確認してください\n"
                f"詳細: {e}"
            ) from e
