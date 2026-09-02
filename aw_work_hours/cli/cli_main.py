"""メインCLI処理"""

import sys
from datetime import date

from ..types import APIConnectionError, CLIError
from ..settings import Settings
from ..domain.afk_bucket import AFKBucket
from ..domain.month_period import MonthPeriod
from ..domain.work_period_report import WorkPeriodReport
from ..web.work_http_server import WorkHTTPServer
from .cli_args import CLIArgs
from .cli_output import CLIOutput


class CLIMain:
    """メインCLI処理"""

    def __init__(self) -> None:
        self._args: CLIArgs = CLIArgs()

    def run(self) -> None:
        try:
            settings: Settings = Settings()
            self._apply_args(settings)
            if self._args.html:
                self._run_html(settings)
            else:
                self._run_text(settings)
        except (CLIError, APIConnectionError) as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)

    def _apply_args(self, settings: Settings) -> None:
        changed: bool = False
        if self._args.no_colon:
            settings.no_colon = True
            changed = True
        if self._args.min_event is not None:
            settings.min_event_seconds = self._args.min_event
            changed = True
        if self._args.bucket is not None:
            settings.bucket = self._args.bucket
            changed = True
        if changed:
            settings.save()

    def _run_html(self, settings: Settings) -> None:
        bucket: AFKBucket = AFKBucket(settings.bucket)
        bucket.id  # 起動前にバケット解決を検証（失敗時はCLIError/APIConnectionError）
        init_month: str | None = None
        if self._args.month not in ("this", "all"):
            dates: list[date] = MonthPeriod(self._args.month).date_range()
            if dates:
                init_month = f"{dates[0].year}-{dates[0].month:02d}"
        server: WorkHTTPServer = WorkHTTPServer()
        server.start(init_month, self._args.quiet, bucket)

    def _run_text(self, settings: Settings) -> None:
        period: MonthPeriod = MonthPeriod(self._args.month)
        labels: dict[str, str] = {"all": "全期間", "this": "今月", "last": "先月"}
        self._status(f"対象期間: {labels.get(self._args.month, self._args.month)}")
        self._status("ActivityWatchからデータを取得中...")
        bucket: AFKBucket = AFKBucket(settings.bucket)
        report: WorkPeriodReport = WorkPeriodReport(
            period, bucket, settings.min_event_seconds
        )
        self._status(f"取得イベント数: {len(report.events.raw)}")
        self._status(f"勤務日数: {report.calendar.days}")
        output: CLIOutput = CLIOutput(self._args, settings)
        output.run(report)

    def _status(self, msg: str) -> None:
        if not self._args.quiet:
            print(msg, file=sys.stderr)
