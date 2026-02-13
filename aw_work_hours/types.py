"""定数・例外・型定義"""

from typing import TypedDict
from zoneinfo import ZoneInfo

_API_BASE: str = "http://127.0.0.1:5600/api/0"
_TIMEZONE: ZoneInfo = ZoneInfo("Asia/Tokyo")
_WEEKDAYS: list[str] = ["月", "火", "水", "木", "金", "土", "日"]


class CLIError(Exception):
    """ユーザー入力や設定のエラー（引数不正・バケット未発見など）"""


class APIConnectionError(Exception):
    """ActivityWatch APIへの接続エラー"""


class AWEvent(TypedDict):
    """ActivityWatch APIから取得するイベント"""

    timestamp: str
    duration: float
    data: dict[str, str]


class HTMLEvent(TypedDict):
    """HTML UI用のイベントデータ"""

    startH: int
    startM: int
    startS: int
    endH: int
    endM: int
    endS: int
    duration: float
    data: dict[str, str]
