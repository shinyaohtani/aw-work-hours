"""コマンドライン引数"""

import argparse


class CLIArgs:
    """コマンドライン引数"""

    def __init__(self) -> None:
        self._args: argparse.Namespace = self._parse()

    def _parse(self) -> argparse.Namespace:
        p: argparse.ArgumentParser = argparse.ArgumentParser(
            description="ActivityWatchから勤務時間をCSVにエクスポート",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._epilog(),
        )
        p.add_argument(
            "--month",
            "-m",
            default="this",
            help="対象月: this(今月), last(先月), all(全期間), YYYY-MM",
        )
        p.add_argument("--output", "-o", help="出力ファイル名")
        p.add_argument("--quiet", "-q", action="store_true", help="進捗非表示")
        p.add_argument(
            "--no-colon", action="store_true", help="時刻をHHMMで出力（stdout時のみ）"
        )
        p.add_argument("--html", action="store_true", help="HTML形式でブラウザ表示")
        p.add_argument(
            "--bucket", "-b", help="使用するAFKバケットのPC名（例: Mac, PC-NAME.local）"
        )
        p.add_argument(
            "--min-event",
            type=int,
            default=None,
            help="最小イベント秒数（デフォルト: 150）",
        )
        return p.parse_args()

    _EPILOG: str = "\n".join(
        [
            "例:",
            "  aw-work-hours                    今月の勤務時間を出力",
            "  aw-work-hours --month=last       先月の勤務時間を出力",
            "  aw-work-hours --month=2025-11    2025年11月の勤務時間を出力",
            "  aw-work-hours --month=all        全期間の勤務時間を出力",
            "  aw-work-hours -o work.csv        ファイルに出力",
        ]
    )

    def _epilog(self) -> str:
        return self._EPILOG

    @property
    def month(self) -> str:
        return self._args.month

    @property
    def output(self) -> str | None:
        return self._args.output

    @property
    def quiet(self) -> bool:
        return self._args.quiet

    @property
    def no_colon(self) -> bool:
        return self._args.no_colon

    @property
    def html(self) -> bool:
        return self._args.html

    @property
    def bucket(self) -> str | None:
        return self._args.bucket

    @property
    def min_event(self) -> int | None:
        return self._args.min_event
