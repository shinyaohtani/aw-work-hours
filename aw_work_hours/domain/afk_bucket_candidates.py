"""AFKバケットの候補群"""

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime

from ..types import _API_BASE, _TIMEZONE, AWEvent, CLIError


class AFKBucketCandidates:
    """AFKバケットの候補群"""

    def __init__(self, afk_ids: list[str], preference: str | None) -> None:
        self._afk_ids: list[str] = afk_ids
        self._preference: str | None = preference

    @property
    def selected(self) -> str:
        if not self._afk_ids:
            raise CLIError(
                "エラー: AFKバケットが見つかりません\n"
                "aw-watcher-afkが有効か確認してください"
            )
        if self._preference:
            return self._by_preference()
        if len(self._afk_ids) == 1:
            return self._afk_ids[0]
        return self._by_latest()

    def _by_preference(self) -> str:
        pref: str = self._preference or ""
        matched: list[str] = [b for b in self._afk_ids if pref.lower() in b.lower()]
        if not matched:
            lines: list[str] = [
                f"エラー: '{self._preference}' にマッチするバケットが見つかりません",
                "利用可能なバケット:",
            ]
            for bid in self._afk_ids:
                lines.append(f"  {bid.replace('aw-watcher-afk_', '')}")
            raise CLIError("\n".join(lines))
        if len(matched) > 1:
            lines = [
                f"エラー: '{self._preference}' に複数のバケットがマッチしました:",
            ]
            for bid in matched:
                lines.append(f"  {bid.replace('aw-watcher-afk_', '')}")
            raise CLIError("\n".join(lines))
        return matched[0]

    def _by_latest(self) -> str:
        ranked: list[tuple[str, datetime | None, str]] = []
        for bid in self._afk_ids:
            hostname: str = bid.replace("aw-watcher-afk_", "")
            ranked.append((bid, self._last_event(bid), hostname))
        ranked.sort(
            key=lambda x: x[1] or datetime.min.replace(tzinfo=_TIMEZONE), reverse=True
        )
        # 複数バケット検出時の情報表示（候補の詳細はここでしか参照できない）
        print(
            "複数のAFKバケットが見つかりました（PC名ごとに記録が分かれています）:",
            file=sys.stderr,
        )
        for i, (_, last, hostname) in enumerate(ranked):
            last_str: str = last.strftime("%Y-%m-%d %H:%M") if last else "データなし"
            marker: str = " ← 使用" if i == 0 else ""
            print(f"  {hostname}: 最終記録 {last_str}{marker}", file=sys.stderr)
        print("最新のデータを持つバケットを自動選択しました。", file=sys.stderr)
        print("特定のバケットを使う場合: --bucket=PC名", file=sys.stderr)
        return ranked[0][0]

    def _last_event(self, bucket_id: str) -> datetime | None:
        url: str = f"{_API_BASE}/buckets/{bucket_id}/events?limit=1"
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                events: list[AWEvent] = json.loads(resp.read().decode())
                if events:
                    return datetime.fromisoformat(events[0]["timestamp"]).astimezone(
                        _TIMEZONE
                    )
        except (urllib.error.URLError, KeyError, IndexError):
            # Ignore failures when fetching/parsing the last event and treat as "no data"
            pass
        return None
