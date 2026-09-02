"""ActivityWatchのAFKバケット"""

import json
import urllib.error
import urllib.request

from ..types import _API_BASE, APIConnectionError
from .afk_bucket_candidates import AFKBucketCandidates
from .afk_bucket_id import AFKBucketId


class AFKBucket:
    """ActivityWatchのAFKバケット（選択・キャッシュ）"""

    def __init__(self, preference: str | None, timeout: int = 10) -> None:
        self._preference: str | None = preference
        self._timeout: int = timeout
        self._cached_id: str | None = None

    @property
    def id(self) -> str:
        if self._cached_id is None:
            self._cached_id = AFKBucketCandidates(
                self.candidates, self._preference
            ).selected.raw
        resolved: str = self._cached_id
        return resolved

    @property
    def candidates(self) -> list[AFKBucketId]:
        url: str = f"{_API_BASE}/buckets"
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:
                buckets: dict[str, object] = json.loads(resp.read().decode())
        except urllib.error.URLError as e:
            raise APIConnectionError(
                "エラー: ActivityWatch APIに接続できません\n"
                "ActivityWatchが起動しているか確認してください\n"
                f"詳細: {e}"
            ) from e
        return [b for b in (AFKBucketId(name) for name in buckets) if b.is_afk_bucket]
