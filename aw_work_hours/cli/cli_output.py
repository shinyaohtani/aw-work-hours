"""CLI出力処理"""

import subprocess
import sys
from datetime import date

from ..settings import Settings
from ..domain.holiday_calendar import HolidayCalendar
from ..domain.work_period_report import WorkPeriodReport
from ..output.epoch_script import EpochScript
from ..output.work_csv import WorkCSV
from ..output.work_text import WorkText
from .cli_args import CLIArgs


class CLIOutput:
    """CLI出力処理"""

    def __init__(self, args: CLIArgs, settings: Settings) -> None:
        self._args: CLIArgs = args
        self._settings: Settings = settings

    def run(self, report: WorkPeriodReport) -> None:
        holidays: HolidayCalendar = HolidayCalendar()
        if self._args.epoch:
            self._copy_epoch_script(report)
        elif self._args.output:
            self._write_csv(report)
        else:
            self._print_text(report, holidays)

    def _write_csv(self, report: WorkPeriodReport) -> None:
        csv: WorkCSV = WorkCSV(report)
        assert self._args.output is not None
        output_abspath: str = self._args.output
        with open(output_abspath, "w", encoding="utf-8-sig") as f:
            f.write(csv.content())
        self._status(f"出力完了: {output_abspath}")

    def _copy_epoch_script(self, report: WorkPeriodReport) -> None:
        script: EpochScript = EpochScript(
            report, self._settings.break_rule, date.today()
        )
        subprocess.run(["pbcopy"], input=script.content().encode("utf-8"), check=True)
        self._status(
            f"epoch入力スクリプトをクリップボードにコピーしました（{len(script.days)}日分）"
        )
        self._status("勤務実績入力画面の開発者ツールのコンソールに貼り付けて実行してください")

    def _print_text(self, report: WorkPeriodReport, holidays: HolidayCalendar) -> None:
        text: WorkText = WorkText(report, holidays, self._settings.no_colon)
        print(text.content(), end="")

    def _status(self, msg: str) -> None:
        if not self._args.quiet:
            print(msg, file=sys.stderr)
