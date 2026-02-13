"""日本の祝日カレンダー（キャッシュ付き）"""

import json
import urllib.error
import urllib.request
from datetime import date

import truststore

truststore.inject_into_ssl()

from .. import PROJECT_DIR


class HolidayCalendar:
    """日本の祝日カレンダー（キャッシュ付き）"""

    _API_URL: str = "https://holidays-jp.github.io/api/v1/{year}/date.json"

    def __init__(self) -> None:
        self._cache_dir = PROJECT_DIR / "holiday_cache"
        self._holidays: dict[int, set[date]] = {}

    def is_holiday(self, d: date) -> bool:
        return d.weekday() >= 5 or self._is_national(d)

    def _is_national(self, d: date) -> bool:
        if d.year not in self._holidays:
            self._load_year(d.year)
        return d in self._holidays.get(d.year, set())

    def _load_year(self, year: int) -> None:
        cache_file = self._cache_dir / f"{year}.json"
        if cache_file.exists():
            self._holidays[year] = self._parse_cache(cache_file)
        else:
            self._holidays[year] = self._fetch_and_cache(year, cache_file)

    def _parse_cache(self, cache_file) -> set[date]:  # type: ignore[type-arg]
        with open(cache_file, encoding="utf-8") as f:
            return {date.fromisoformat(d) for d in json.load(f).keys()}

    def _fetch_and_cache(self, year: int, cache_file) -> set[date]:  # type: ignore[type-arg]
        url: str = self._API_URL.format(year=year)
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                raw: bytes = resp.read()
                holidays: dict[str, str] = json.loads(raw.decode("utf-8"))
            self._cache_dir.mkdir(exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(raw.decode("utf-8") + "\n")
            return {date.fromisoformat(d) for d in holidays.keys()}
        except urllib.error.URLError:
            # 祝日API接続失敗は致命的でないため空を返す（表示上の差異のみ）
            return set()
