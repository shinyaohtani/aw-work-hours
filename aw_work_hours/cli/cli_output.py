"""CLI出力処理"""

import sys

from ..settings import Settings
from ..domain.holiday_calendar import HolidayCalendar
from ..domain.work_period_report import WorkPeriodReport
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
        if self._args.output:
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

    def _print_text(self, report: WorkPeriodReport, holidays: HolidayCalendar) -> None:
        text: WorkText = WorkText(report, holidays, self._settings.no_colon)
        print(text.content(), end="")

    def _status(self, msg: str) -> None:
        if not self._args.quiet:
            print(msg, file=sys.stderr)
