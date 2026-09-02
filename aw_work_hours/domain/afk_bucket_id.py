"""AFKバケットの識別子"""


class AFKBucketId:
    """AFKバケットの識別子（ホスト名を含む生のID）"""

    _PREFIX: str = "aw-watcher-afk_"

    def __init__(self, raw: str) -> None:
        self._raw: str = raw

    @property
    def raw(self) -> str:
        return self._raw

    @property
    def hostname(self) -> str:
        return self._raw.replace(self._PREFIX, "")

    def matches(self, preference: str) -> bool:
        return preference.lower() in self._raw.lower()

    @classmethod
    def is_afk_bucket(cls, raw: str) -> bool:
        return raw.startswith(cls._PREFIX)
