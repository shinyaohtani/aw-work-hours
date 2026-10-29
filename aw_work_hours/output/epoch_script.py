"""epoch勤務実績入力画面に貼り付ける入力スクリプト"""

import json
from datetime import date
from pathlib import Path

from ..types import EpochDay
from ..domain.break_rule import BreakRule
from ..domain.work_breaks import WorkBreaks
from ..domain.work_moment import WorkMoment
from ..domain.work_period_report import WorkPeriodReport
from ..domain.work_span import WorkSpan


class EpochScript:
    """epoch勤務実績入力画面に貼り付ける入力スクリプト（今日より前の勤務日のみ）"""

    _TEMPLATE_ABSPATH: Path = Path(__file__).with_name("epoch_fill.js")
    _PLACEHOLDER: str = "__AW_DAYS__"

    def __init__(self, report: WorkPeriodReport, rule: BreakRule, today: date) -> None:
        self._report: WorkPeriodReport = report
        self._rule: BreakRule = rule
        self._today: date = today

    def content(self) -> str:
        template: str = self._TEMPLATE_ABSPATH.read_text(encoding="utf-8")
        days_json: str = json.dumps(self.days, ensure_ascii=False, indent=2)
        return template.replace(self._PLACEHOLDER, days_json)

    @property
    def days(self) -> dict[str, EpochDay]:
        breaks: dict[date, list[WorkSpan]] = WorkBreaks(
            self._report.events, self._rule
        ).by_day
        daily: dict[date, WorkSpan] = self._report.calendar.daily
        return {
            d.strftime("%Y%m%d"): self._day(d, daily[d], breaks.get(d, []))
            for d in sorted(daily)
            if d < self._today
        }

    def _day(self, d: date, span: WorkSpan, breaks: list[WorkSpan]) -> EpochDay:
        return {
            "start": WorkMoment(span.start).hhmm(d, colon=False),
            "end": WorkMoment(span.end).hhmm(d, colon=False),
            "breaks": [
                [WorkMoment(b.start).hhmm(d, colon=False), WorkMoment(b.end).hhmm(d, colon=False)]
                for b in breaks
            ],
        }
