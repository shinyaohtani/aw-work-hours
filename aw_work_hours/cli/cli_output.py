"""CLI出力処理"""

import sys

from ..settings import Settings
from ..domain.daily_work import DailyWork
from ..domain.holiday_calendar import HolidayCalendar
from ..domain.month_period import MonthPeriod
from ..domain.work_calendar import WorkCalendar
from ..output.work_csv import WorkCSV
from ..output.work_text import WorkText
from .cli_args import CLIArgs


class CLIOutput:
    """CLI出力処理"""

    def __init__(self, args: CLIArgs, settings: Settings) -> None:
        self._args: CLIArgs = args
        self._settings: Settings = settings

    def run(
        self, calendar: WorkCalendar, daily_work: DailyWork, period: MonthPeriod
    ) -> None:
        holidays: HolidayCalendar = HolidayCalendar()
        if self._args.output:
            self._write_csv(calendar, daily_work, period)
        else:
            self._print_text(calendar, daily_work, period, holidays)

    def _write_csv(
        self, calendar: WorkCalendar, daily_work: DailyWork, period: MonthPeriod
    ) -> None:
        csv: WorkCSV = WorkCSV(
            calendar.daily, daily_work.active, daily_work.gaps, period
        )
        assert self._args.output is not None
        output_abspath: str = self._args.output
        with open(output_abspath, "w", encoding="utf-8-sig") as f:
            f.write(csv.content())
        self._status(f"出力完了: {output_abspath}")

    def _print_text(
        self,
        calendar: WorkCalendar,
        daily_work: DailyWork,
        period: MonthPeriod,
        holidays: HolidayCalendar,
    ) -> None:
        text: WorkText = WorkText(
            calendar.daily,
            daily_work.active,
            daily_work.gaps,
            period,
            holidays,
            self._settings.no_colon,
        )
        print(text.content(), end="")

    def _status(self, msg: str) -> None:
        if not self._args.quiet:
            print(msg, file=sys.stderr)
