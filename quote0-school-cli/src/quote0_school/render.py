from __future__ import annotations

from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .calendar_data import CalendarStatus, status_for

WIDTH = 296
HEIGHT = 152

FONT_CANDIDATES = (
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
)


def find_font() -> Path:
    for candidate in FONT_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            return path
    raise FileNotFoundError(
        "未找到中文字体。请安装 PingFang、Noto Sans CJK 或文泉驿正黑。"
    )


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = find_font()
    # PingFang TTC index 0/1 both support Chinese. Synthetic bold is applied by stroke.
    result = ImageFont.truetype(str(path), size=size, index=0)
    result._quote0_bold = bold  # type: ignore[attr-defined]
    return result


def text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    face: ImageFont.FreeTypeFont,
    *,
    anchor: str | None = None,
    fill: int = 0,
) -> None:
    bold = bool(getattr(face, "_quote0_bold", False))
    draw.text(
        xy,
        value,
        font=face,
        fill=fill,
        anchor=anchor,
        stroke_width=1 if bold else 0,
        stroke_fill=fill,
    )


def _format_day(value: date) -> str:
    return f"{value.month:02d}.{value.day:02d}"


def _draw_progress(draw: ImageDraw.ImageDraw, status: CalendarStatus) -> None:
    x0, x1, y = 188, 283, 108
    draw.rounded_rectangle((x0, y, x1, y + 8), radius=4, outline=0, width=1)
    inner_width = max(2, round((x1 - x0 - 4) * status.progress_percent / 100))
    draw.rounded_rectangle(
        (x0 + 2, y + 2, x0 + 2 + inner_width, y + 6), radius=2, fill=0
    )


def render_calendar(day: date, output: Path) -> dict[str, object]:
    status = status_for(day)
    image = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    small = font(10)
    tiny = font(8)
    label = font(13, bold=True)
    value_font = font(62, bold=True)
    unit = font(11, bold=True)
    secondary = font(15, bold=True)

    period_name = status.period.name if status.period else "校历"
    school_year = status.period.school_year if status.period else "上海"
    text(draw, (11, 9), f"上海中小学 · {period_name}", small)
    text(draw, (285, 9), f"{day:%Y.%m.%d}", tiny, anchor="ra")
    draw.line((11, 27, 285, 27), fill=0, width=1)

    text(draw, (12, 38), status.primary_label, label)
    primary = "--" if status.primary_value is None else str(status.primary_value)
    text(draw, (8, 102), primary, value_font, anchor="ls")
    value_box = draw.textbbox(
        (8, 102), primary, font=value_font, anchor="ls", stroke_width=1
    )
    unit_x = min(154, value_box[2] + 7)
    text(draw, (unit_x, 98), "天", unit, anchor="ls")

    draw.line((175, 37, 175, 136), fill=0, width=1)

    secondary_value = (
        "" if status.secondary_value is None else str(status.secondary_value)
    )
    text(draw, (188, 43), status.secondary_label, tiny)
    text(draw, (188, 66), f"{secondary_value} 天".strip(), secondary)

    if status.period and status.period.kind == "term":
        detail = f"第 {status.teaching_week} 周  ·  {status.progress_percent}%"
        end_label = f"{_format_day(status.period.end)} 结课"
    elif status.period:
        detail = f"假期进度  {status.progress_percent}%"
        end_label = (
            f"{_format_day(status.next_period.start)} 开学"
            if status.next_period
            else f"{_format_day(status.period.end)} 结束"
        )
    else:
        detail = "等待进入已收录校历"
        end_label = (
            _format_day(status.next_period.start) if status.next_period else "待更新"
        )

    text(draw, (188, 82), detail, tiny)
    _draw_progress(draw, status)
    text(draw, (188, 125), end_label, tiny)

    draw.line((11, 139, 285, 139), fill=0, width=1)
    text(draw, (11, 144), f"{school_year} · 上海市教委校历", tiny)
    text(draw, (285, 144), "QUOTE / SCHOOL", tiny, anchor="ra")

    output.parent.mkdir(parents=True, exist_ok=True)
    # The official API recommends disabling dithering for text images. Emit true 1-bit PNG.
    bitmap = image.point(lambda pixel: 0 if pixel < 180 else 255, mode="1")
    bitmap.save(output, format="PNG", optimize=True)

    return {
        "output": str(output.resolve()),
        "width": WIDTH,
        "height": HEIGHT,
        "mode": bitmap.mode,
        "date": day.isoformat(),
        "period": period_name,
        "primary_label": status.primary_label,
        "primary_value": status.primary_value,
        "secondary_label": status.secondary_label,
        "secondary_value": status.secondary_value,
        "progress_percent": status.progress_percent,
    }
