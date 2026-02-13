"""ActivityWatchのAFKバケット"""

import json
import urllib.error
import urllib.request

from ..types import _API_BASE, APIConnectionError
from .afk_bucket_candidates import AFKBucketCandidates


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
        afk_ids: list[str] = cls.fetch_ids()
        cls._cached_id = cls._resolve(afk_ids)
        return cls._cached_id

    @classmethod
    def fetch_ids(cls) -> list[str]:
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
        return [b for b in buckets if b.startswith("aw-watcher-afk_")]

    @classmethod
    def _resolve(cls, afk_ids: list[str]) -> str:
        candidates: AFKBucketCandidates = AFKBucketCandidates(afk_ids, cls._preference)
        return candidates.selected
