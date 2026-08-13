from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from . import __version__
from .api import (
    ApiError,
    device_status,
    image_payload,
    list_devices,
    list_tasks,
    push_canvas,
    push_image,
    request_json,
)
from .canvas import DEFAULT_LANDING_URL, canvas_payload, render_canvas_preview
from .config import CONFIG_PATH, Config, load_config, save_device
from .render import find_font, render_calendar


class CliError(RuntimeError):
    def __init__(self, message: str, kind: str = "cli_error") -> None:
        super().__init__(message)
        self.kind = kind


def emit(data: Any, *, as_json: bool, message: str | None = None) -> None:
    if as_json:
        print(json.dumps({"ok": True, "data": data}, ensure_ascii=False))
    elif message:
        print(message)
    elif isinstance(data, (dict, list)):
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(data)


def emit_error(error: Exception, *, as_json: bool) -> None:
    kind = getattr(
        error, "kind", "api_error" if isinstance(error, ApiError) else "error"
    )
    if as_json:
        print(
            json.dumps(
                {"ok": False, "error": {"type": kind, "message": str(error)}},
                ensure_ascii=False,
            )
        )
    else:
        print(f"错误：{error}", file=sys.stderr)


def parse_day(value: str | None) -> date:
    if not value:
        return datetime.now(ZoneInfo("Asia/Shanghai")).date()
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise CliError("日期必须使用 YYYY-MM-DD 格式", "validation_error") from error


def require_api_key(config: Config) -> str:
    if not config.api_key:
        raise CliError(
            "缺少 DOT_API_KEY；请先在 Dot. App 创建 API Key 并设置环境变量",
            "config_error",
        )
    return config.api_key


def resolve_device(config: Config, api_key: str) -> str:
    if config.device_id:
        return config.device_id
    devices = [
        item
        for item in list_devices(api_key, base_url=config.base_url)
        if item.get("model") == "quote_0"
    ]
    if len(devices) == 1 and devices[0].get("id"):
        return str(devices[0]["id"])
    if not devices:
        raise CliError("未找到 Quote/0 设备，请设置 DOT_DEVICE_ID", "config_error")
    raise CliError(
        "检测到多个 Quote/0 设备，请设置 DOT_DEVICE_ID 指定目标", "config_error"
    )


def filter_tasks(
    tasks: list[dict[str, Any]], content_type: str
) -> list[dict[str, Any]]:
    if content_type == "all":
        return tasks
    needle = content_type.lower()

    def contains(value: Any) -> bool:
        if isinstance(value, str):
            return needle in value.lower()
        if isinstance(value, dict):
            return any(contains(item) for item in value.values())
        if isinstance(value, list):
            return any(contains(item) for item in value)
        return False

    return [task for task in tasks if contains(task)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quote0-school",
        description="生成上海中小学校历墨水屏画面并推送到 Quote/0。",
    )
    parser.add_argument("--json", action="store_true", help="输出稳定 JSON 包装")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="检查字体、认证与设备配置")

    init = sub.add_parser("init", help="保存默认设备号（不保存 API Key）")
    init.add_argument("--device-id", required=True, help="Quote/0 设备序列号")
    init.add_argument("--base-url", help="可选 API 基础 URL")

    render = sub.add_parser("render", help="生成 296×152 黑白 PNG")
    render.add_argument("--date", help="以 YYYY-MM-DD 渲染；默认今天")
    render.add_argument(
        "--output", type=Path, default=Path("preview.png"), help="PNG 输出路径"
    )

    canvas_preview = sub.add_parser(
        "canvas-preview", help="生成 Canvas API 的 296×152 布局预览"
    )
    canvas_preview.add_argument("--date", help="以 YYYY-MM-DD 渲染；默认今天")
    canvas_preview.add_argument(
        "--output",
        type=Path,
        default=Path("canvas-preview.png"),
        help="PNG 输出路径",
    )

    sub.add_parser("devices", help="列出 API Key 可访问的设备")
    sub.add_parser("status", help="读取默认设备状态")
    tasks = sub.add_parser("tasks", help="列出默认设备的循环内容")
    tasks.add_argument(
        "--type",
        choices=["all", "image", "canvas"],
        default="all",
        help="按 API 内容类型筛选；默认 all",
    )

    push = sub.add_parser("push", help="生成画面并推送到默认 Quote/0")
    push.add_argument("--date", help="以 YYYY-MM-DD 渲染；默认今天")
    push.add_argument("--task-key", help="多个 Image API 内容时指定任务 key")
    push.add_argument(
        "--no-refresh", action="store_true", help="只更新内容，不立即切换显示"
    )
    push.add_argument("--dry-run", action="store_true", help="仅生成并输出请求摘要")
    push.add_argument("--output", type=Path, help="同时保留生成的 PNG")

    push_canvas_parser = sub.add_parser(
        "push-canvas", help="通过官方 Canvas API 推送结构化校历"
    )
    push_canvas_parser.add_argument("--date", help="以 YYYY-MM-DD 生成；默认今天")
    push_canvas_parser.add_argument(
        "--no-refresh", action="store_true", help="只更新内容，不立即切换显示"
    )
    push_canvas_parser.add_argument(
        "--dry-run", action="store_true", help="仅输出完整 Canvas 请求，不访问设备"
    )
    push_canvas_parser.add_argument(
        "--link",
        default=DEFAULT_LANDING_URL,
        help="点击内容时打开的落地页 URL",
    )
    push_canvas_parser.add_argument(
        "--preview", type=Path, help="同时保存 296×152 Canvas 布局预览"
    )

    request = sub.add_parser("request", help="执行认证后的原始只读请求")
    request.add_argument("method", choices=["get", "GET"], help="仅支持 GET")
    request.add_argument("path", help="API 路径，如 /api/authV2/open/devices")
    return parser


def run(args: argparse.Namespace) -> Any:
    config = load_config()

    if args.command == "doctor":
        try:
            font_path = str(find_font())
            font_ok = True
        except FileNotFoundError:
            font_path = None
            font_ok = False
        return {
            "version": __version__,
            "python": sys.version.split()[0],
            "font_ok": font_ok,
            "font": font_path,
            "api_key": {
                "available": bool(config.api_key),
                "source": config.api_key_source,
            },
            "device_id": {
                "available": bool(config.device_id),
                "source": config.device_id_source,
            },
            "config_path": str(CONFIG_PATH),
            "base_url": config.base_url,
            "ready_to_render": font_ok,
            "ready_to_push": font_ok and bool(config.api_key),
        }

    if args.command == "init":
        path = save_device(args.device_id, args.base_url)
        return {
            "config_path": str(path),
            "device_id": args.device_id,
            "api_key_saved": False,
        }

    if args.command == "render":
        return render_calendar(parse_day(args.date), args.output)

    if args.command == "canvas-preview":
        return render_canvas_preview(parse_day(args.date), args.output)

    if args.command == "push" and args.dry_run:
        device_id = config.device_id or "auto-discover"
        with tempfile.TemporaryDirectory(prefix="quote0-school-") as temp_dir:
            output = args.output or Path(temp_dir) / "calendar.png"
            render_info = render_calendar(parse_day(args.date), output)
            payload = image_payload(
                output,
                refresh_now=not args.no_refresh,
                task_key=args.task_key,
            )
            return {
                "dry_run": True,
                "device_id": device_id,
                "render": render_info,
                "request": {
                    "endpoint": f"/api/authV2/open/device/{device_id}/image",
                    "refresh_now": payload["refreshNow"],
                    "dither_type": payload["ditherType"],
                    "task_alias": payload["taskAlias"],
                    "task_key": payload.get("taskKey"),
                    "image_bytes": output.stat().st_size,
                },
            }

    if args.command == "push-canvas" and args.dry_run:
        day = parse_day(args.date)
        payload = canvas_payload(
            day,
            refresh_now=not args.no_refresh,
            landing_url=args.link,
        )
        preview = render_canvas_preview(day, args.preview) if args.preview else None
        device_id = config.device_id or "auto-discover"
        return {
            "dry_run": True,
            "device_id": device_id,
            "preview": preview,
            "request": {
                "endpoint": f"/api/authV2/open/device/{device_id}/canvas",
                "payload": payload,
            },
        }

    api_key = require_api_key(config)

    if args.command == "devices":
        return list_devices(api_key, base_url=config.base_url)

    if args.command == "status":
        device_id = resolve_device(config, api_key)
        return device_status(api_key, device_id, base_url=config.base_url)

    if args.command == "tasks":
        device_id = resolve_device(config, api_key)
        return filter_tasks(
            list_tasks(api_key, device_id, base_url=config.base_url),
            args.type,
        )

    if args.command == "request":
        return request_json("GET", args.path, api_key, base_url=config.base_url)

    if args.command == "push":
        with tempfile.TemporaryDirectory(prefix="quote0-school-") as temp_dir:
            output = args.output or Path(temp_dir) / "calendar.png"
            render_info = render_calendar(parse_day(args.date), output)
            resolved_id = resolve_device(config, api_key)
            result = push_image(
                api_key,
                resolved_id,
                output,
                base_url=config.base_url,
                refresh_now=not args.no_refresh,
                task_key=args.task_key,
            )
            return {"device_id": resolved_id, "render": render_info, "response": result}

    if args.command == "push-canvas":
        day = parse_day(args.date)
        payload = canvas_payload(
            day,
            refresh_now=not args.no_refresh,
            landing_url=args.link,
        )
        preview = render_canvas_preview(day, args.preview) if args.preview else None
        resolved_id = resolve_device(config, api_key)
        result = push_canvas(
            api_key,
            resolved_id,
            payload,
            base_url=config.base_url,
        )
        return {"device_id": resolved_id, "preview": preview, "response": result}

    raise CliError("未知命令")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run(args)
        message = None
        if args.command == "render" and not args.json:
            message = f"已生成：{result['output']}（{result['width']}×{result['height']}，{result['period']}）"
        elif args.command == "canvas-preview" and not args.json:
            message = f"已生成 Canvas 预览：{result['output']}（{result['width']}×{result['height']}）"
        elif args.command == "push" and not args.json:
            message = (
                "推送请求已完成。"
                if not result.get("dry_run")
                else json.dumps(result, ensure_ascii=False, indent=2)
            )
        elif args.command == "push-canvas" and not args.json:
            message = (
                "Canvas 推送请求已完成。"
                if not result.get("dry_run")
                else json.dumps(result, ensure_ascii=False, indent=2)
            )
        emit(result, as_json=args.json, message=message)
    except (CliError, ApiError, FileNotFoundError, OSError) as error:
        emit_error(error, as_json=args.json)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
