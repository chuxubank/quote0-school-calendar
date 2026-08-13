from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from .calendar_data import CalendarStatus, status_for
from .render import HEIGHT, WIDTH, font, text

DEFAULT_LANDING_URL = "https://asahiart.github.io/quote0-school-calendar/"


def _short_date(value: date) -> str:
    return f"{value.month:02d}.{value.day:02d}"


def _full_date(value: date) -> str:
    return f"{value.year}.{value.month:02d}.{value.day:02d}"


def _detail(status: CalendarStatus) -> str:
    if status.period and status.period.kind == "term":
        return f"第 {status.teaching_week} 周 · 学期进度"
    if status.period:
        return f"{status.period.name}进度"
    return "等待校历更新"


def _next_event(status: CalendarStatus) -> str:
    if status.period and status.next_period:
        label = status.period.next_label or f"{status.next_period.name}开始"
        return f"{_short_date(status.next_period.start)} {label}"
    if status.period:
        return f"{_short_date(status.period.end)} 结束"
    if status.next_period:
        return f"{_short_date(status.next_period.start)} {status.next_period.name}开始"
    return "校历待更新"


def canvas_data(day: date) -> dict[str, Any]:
    status = status_for(day)
    return {
        "date": _full_date(day),
        "phase": status.period.name if status.period else "校历",
        "primaryLabel": status.primary_label,
        "primaryValue": status.primary_value
        if status.primary_value is not None
        else "--",
        "secondaryLabel": status.secondary_label,
        "secondaryValue": status.secondary_value
        if status.secondary_value is not None
        else "--",
        "progress": status.progress_percent,
        "detail": _detail(status),
        "nextEvent": _next_event(status),
    }


def canvas_template() -> dict[str, list[dict[str, Any]]]:
    return {
        "default": [
            {
                "type": "div",
                "props": {
                    "tw": "flex flex-col w-full h-full min-w-0 min-h-0 bg-white text-black gap-[5px]",
                    "children": [
                        {
                            "type": "div",
                            "props": {
                                "tw": "flex flex-row items-center justify-between shrink-0 text-9-chillduansans",
                                "children": [
                                    {
                                        "type": "span",
                                        "props": {
                                            "tw": "font-bold",
                                            "children": '沪上校历 · {{get inputData "phase" default="校历"}}',
                                        },
                                    },
                                    {
                                        "type": "span",
                                        "props": {
                                            "children": '{{get inputData "date" default="--"}}'
                                        },
                                    },
                                ],
                            },
                        },
                        {
                            "type": "div",
                            "props": {
                                "tw": "w-full h-px bg-black shrink-0",
                                "children": "",
                            },
                        },
                        {
                            "type": "div",
                            "props": {
                                "tw": "flex flex-row flex-1 min-h-0 gap-[10px]",
                                "children": [
                                    {
                                        "type": "div",
                                        "props": {
                                            "tw": "flex flex-col flex-[3] min-w-0 justify-center",
                                            "children": [
                                                {
                                                    "type": "span",
                                                    "props": {
                                                        "tw": "text-11-chillduansans font-bold",
                                                        "children": '{{get inputData "primaryLabel" default="今日"}}',
                                                    },
                                                },
                                                {
                                                    "type": "div",
                                                    "props": {
                                                        "tw": "flex flex-row items-end gap-[4px]",
                                                        "children": [
                                                            {
                                                                "type": "span",
                                                                "props": {
                                                                    "tw": "text-52-chillduansans font-bold leading-none",
                                                                    "children": '{{get inputData "primaryValue" default="--"}}',
                                                                },
                                                            },
                                                            {
                                                                "type": "span",
                                                                "props": {
                                                                    "tw": "text-11-chillduansans font-bold pb-[4px]",
                                                                    "children": "天",
                                                                },
                                                            },
                                                        ],
                                                    },
                                                },
                                            ],
                                        },
                                    },
                                    {
                                        "type": "div",
                                        "props": {
                                            "tw": "w-px h-full bg-black shrink-0",
                                            "children": "",
                                        },
                                    },
                                    {
                                        "type": "div",
                                        "props": {
                                            "tw": "flex flex-col flex-[2] min-w-0 justify-center gap-[5px]",
                                            "children": [
                                                {
                                                    "type": "span",
                                                    "props": {
                                                        "tw": "text-9-chillduansans",
                                                        "children": '{{get inputData "secondaryLabel" default="进度"}}',
                                                    },
                                                },
                                                {
                                                    "type": "span",
                                                    "props": {
                                                        "tw": "text-20-chillduansans font-bold leading-none",
                                                        "children": '{{get inputData "secondaryValue" default="--"}} 天',
                                                    },
                                                },
                                                {
                                                    "type": "span",
                                                    "props": {
                                                        "tw": "text-9-chillduansans",
                                                        "children": '{{get inputData "detail" default="上海中小学"}}',
                                                    },
                                                },
                                                {
                                                    "type": "div",
                                                    "props": {
                                                        "tw": "flex flex-row items-center gap-[4px]",
                                                        "children": [
                                                            {
                                                                "type": "div",
                                                                "props": {
                                                                    "tw": "w-[58px] h-[5px] border border-black",
                                                                    "children": "",
                                                                },
                                                            },
                                                            {
                                                                "type": "span",
                                                                "props": {
                                                                    "tw": "text-8-chillduansans font-bold",
                                                                    "children": '{{get inputData "progress" default="0"}}%',
                                                                },
                                                            },
                                                        ],
                                                    },
                                                },
                                                {
                                                    "type": "span",
                                                    "props": {
                                                        "tw": "text-8-chillduansans",
                                                        "children": '{{get inputData "nextEvent" default=""}}',
                                                    },
                                                },
                                            ],
                                        },
                                    },
                                ],
                            },
                        },
                        {
                            "type": "div",
                            "props": {
                                "tw": "flex flex-row items-center justify-between shrink-0 text-8-chillduansans",
                                "children": [
                                    {
                                        "type": "span",
                                        "props": {"children": "上海市教委校历"},
                                    },
                                    {
                                        "type": "span",
                                        "props": {"children": "QUOTE / SCHOOL"},
                                    },
                                ],
                            },
                        },
                    ],
                },
            }
        ]
    }


def canvas_payload(
    day: date,
    *,
    refresh_now: bool = True,
    landing_url: str = DEFAULT_LANDING_URL,
) -> dict[str, Any]:
    return {
        "refreshNow": refresh_now,
        "taskAlias": "沪上校历",
        "data": canvas_data(day),
        "windowData": canvas_template(),
        "layoutFull": {"tw": "p-[10px]"},
        "link": landing_url.rstrip("/") + "/",
        "border": 0,
    }


def render_canvas_preview(day: date, output: Path) -> dict[str, object]:
    data = canvas_data(day)
    image = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    tiny = font(8)
    small = font(9)
    label = font(11)
    value = font(52, bold=True)
    unit = font(11, bold=True)
    secondary = font(20, bold=True)

    text(draw, (10, 10), f"沪上校历 · {data['phase']}", small)
    text(draw, (286, 10), str(data["date"]), small, anchor="ra")
    draw.line((10, 25, 286, 25), fill=0, width=1)

    text(draw, (12, 42), str(data["primaryLabel"]), label)
    primary = str(data["primaryValue"])
    text(draw, (10, 105), primary, value, anchor="ls")
    value_box = draw.textbbox(
        (10, 105), primary, font=value, anchor="ls", stroke_width=1
    )
    text(draw, (min(153, value_box[2] + 5), 101), "天", unit, anchor="ls")

    draw.line((174, 35, 174, 128), fill=0, width=1)
    text(draw, (185, 42), str(data["secondaryLabel"]), small)
    text(draw, (185, 54), f"{data['secondaryValue']} 天", secondary)
    text(draw, (185, 82), str(data["detail"]), small)

    progress = int(data["progress"])
    draw.rectangle((185, 94, 244, 100), outline=0, width=1)
    text(draw, (251, 99), f"{progress}%", tiny, anchor="lm")
    text(draw, (185, 116), str(data["nextEvent"]), tiny)

    text(draw, (10, 142), "上海市教委校历", tiny)
    text(draw, (286, 142), "QUOTE / SCHOOL", tiny, anchor="ra")

    output.parent.mkdir(parents=True, exist_ok=True)
    bitmap = image.point(lambda pixel: 0 if pixel < 180 else 255, mode="1")
    bitmap.save(output, format="PNG", optimize=True)
    return {
        "output": str(output.resolve()),
        "width": WIDTH,
        "height": HEIGHT,
        "mode": bitmap.mode,
        "date": day.isoformat(),
        "api": "canvas",
        "data": data,
    }
