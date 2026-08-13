from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Period:
    key: str
    school_year: str
    name: str
    start: date
    end: date
    kind: str
    weeks: int | None = None
    next_label: str | None = None


PERIODS = (
    Period(
        "term-2025-1",
        "2025学年",
        "第一学期",
        date(2025, 9, 1),
        date(2026, 1, 30),
        "term",
        22,
    ),
    Period(
        "winter-2026",
        "2025学年",
        "寒假",
        date(2026, 1, 31),
        date(2026, 3, 1),
        "vacation",
        next_label="春季开学",
    ),
    Period(
        "term-2025-2",
        "2025学年",
        "第二学期",
        date(2026, 3, 2),
        date(2026, 6, 30),
        "term",
        18,
    ),
    Period(
        "summer-2026",
        "2025学年",
        "暑假",
        date(2026, 7, 1),
        date(2026, 8, 31),
        "vacation",
        next_label="秋季开学",
    ),
    Period(
        "term-2026-1",
        "2026学年",
        "第一学期",
        date(2026, 9, 1),
        date(2027, 1, 22),
        "term",
        21,
    ),
    Period(
        "winter-2027",
        "2026学年",
        "寒假",
        date(2027, 1, 23),
        date(2027, 2, 21),
        "vacation",
        next_label="春季开学",
    ),
    Period(
        "term-2026-2",
        "2026学年",
        "第二学期",
        date(2027, 2, 22),
        date(2027, 6, 30),
        "term",
        19,
    ),
    Period(
        "summer-2027",
        "2026学年",
        "暑假",
        date(2027, 7, 1),
        date(2027, 8, 31),
        "vacation",
    ),
)


@dataclass(frozen=True)
class CalendarStatus:
    today: date
    period: Period | None
    next_period: Period | None
    elapsed_days: int
    remaining_days: int
    progress_percent: int
    teaching_week: int | None
    primary_label: str
    primary_value: int | None
    secondary_label: str
    secondary_value: int | None


def inclusive_days(start: date, end: date) -> int:
    return (end - start).days + 1


def status_for(day: date) -> CalendarStatus:
    period = next((item for item in PERIODS if item.start <= day <= item.end), None)
    if period is None:
        future = next((item for item in PERIODS if day < item.start), None)
        return CalendarStatus(
            today=day,
            period=None,
            next_period=future,
            elapsed_days=0,
            remaining_days=max(0, (future.start - day).days) if future else 0,
            progress_percent=0,
            teaching_week=None,
            primary_label="距下一阶段" if future else "校历待更新",
            primary_value=(future.start - day).days if future else None,
            secondary_label=future.name if future else "请更新数据",
            secondary_value=None,
        )

    index = PERIODS.index(period)
    next_period = PERIODS[index + 1] if index + 1 < len(PERIODS) else None
    total = inclusive_days(period.start, period.end)
    elapsed = inclusive_days(period.start, day)
    remaining = max(0, (period.end - day).days)
    progress = min(100, max(0, round(elapsed / total * 100)))

    if period.kind == "term":
        week = min(period.weeks or 1, ((elapsed - 1) // 7) + 1)
        return CalendarStatus(
            day,
            period,
            next_period,
            elapsed,
            remaining,
            progress,
            week,
            "开学第",
            elapsed,
            "距学期结束",
            remaining,
        )

    days_to_next = (next_period.start - day).days if next_period else remaining
    return CalendarStatus(
        day,
        period,
        next_period,
        elapsed,
        remaining,
        progress,
        None,
        f"距{period.next_label or '假期结束'}",
        days_to_next,
        f"{period.name}第",
        elapsed,
    )
