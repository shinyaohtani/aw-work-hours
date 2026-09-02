"""ActivityWatchのAFKバケット"""

import json
import urllib.error
import urllib.request

from ..types import _API_BASE, APIConnectionError
from .afk_bucket_candidates import AFKBucketCandidates
from .afk_bucket_id import AFKBucketId


class AFKBucket:
    """ActivityWatchのAFKバケット"""

    _cached_id: str | None = None
    _preference: str | None = None

    @classmethod
    def clear_cache(cls) -> None:
        cls._cached_id = None

    @classmethod
    def set_preference(cls, hostname: str | None) -> None:
        cls._preference = hostname

    @classmethod
    def id(cls) -> str:
        if cls._cached_id:
            return cls._cached_id
        afk_ids: list[AFKBucketId] = cls.fetch_ids()
        cls._cached_id = cls._resolve(afk_ids)
        return cls._cached_id

    @classmethod
    def fetch_ids(cls) -> list[AFKBucketId]:
        url: str = f"{_API_BASE}/buckets"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                buckets: dict[str, object] = json.loads(resp.read().decode())
        except urllib.error.URLError as e:
            raise APIConnectionError(
                "エラー: ActivityWatch APIに接続できません\n"
                "ActivityWatchが起動しているか確認してください\n"
                f"詳細: {e}"
            ) from e
        return [AFKBucketId(b) for b in buckets if AFKBucketId.is_afk_bucket(b)]

    @classmethod
    def _resolve(cls, afk_ids: list[AFKBucketId]) -> str:
        candidates: AFKBucketCandidates = AFKBucketCandidates(afk_ids, cls._preference)
        return candidates.selected.raw
