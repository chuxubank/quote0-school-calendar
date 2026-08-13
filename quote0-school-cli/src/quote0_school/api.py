from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://dot.mindreset.tech"


class ApiError(RuntimeError):
    def __init__(self, message: str, *, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


def request_json(
    method: str,
    path: str,
    api_key: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    body: dict[str, Any] | None = None,
) -> Any:
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    payload = json.dumps(body).encode("utf-8") if body is not None else None
    request = Request(
        url,
        data=payload,
        method=method.upper(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "quote0-school-calendar/0.2",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}
    except HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw).get("message", raw)
        except json.JSONDecodeError:
            detail = raw or error.reason
        raise ApiError(
            f"Quote/0 API {error.code}: {detail}", status=error.code
        ) from error
    except URLError as error:
        raise ApiError(f"无法连接 Quote/0 API: {error.reason}") from error


def list_devices(
    api_key: str, *, base_url: str = DEFAULT_BASE_URL
) -> list[dict[str, Any]]:
    result = request_json("GET", "/api/authV2/open/devices", api_key, base_url=base_url)
    if not isinstance(result, list):
        raise ApiError("设备列表响应格式无效")
    return result


def device_status(
    api_key: str, device_id: str, *, base_url: str = DEFAULT_BASE_URL
) -> dict[str, Any]:
    result = request_json(
        "GET",
        f"/api/authV2/open/device/{device_id}/status",
        api_key,
        base_url=base_url,
    )
    if not isinstance(result, dict):
        raise ApiError("设备状态响应格式无效")
    return result


def list_tasks(
    api_key: str, device_id: str, *, base_url: str = DEFAULT_BASE_URL
) -> list[dict[str, Any]]:
    result = request_json(
        "GET",
        f"/api/authV2/open/device/{device_id}/loop/list",
        api_key,
        base_url=base_url,
    )
    if not isinstance(result, list):
        raise ApiError("内容列表响应格式无效")
    return result


def image_payload(
    image_path: Path,
    *,
    refresh_now: bool = True,
    task_key: str | None = None,
) -> dict[str, Any]:
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    payload: dict[str, Any] = {
        "refreshNow": refresh_now,
        "image": encoded,
        "border": 0,
        "ditherType": "NONE",
        "taskAlias": "沪上校历",
    }
    if task_key:
        payload["taskKey"] = task_key
    return payload


def push_image(
    api_key: str,
    device_id: str,
    image_path: Path,
    *,
    base_url: str = DEFAULT_BASE_URL,
    refresh_now: bool = True,
    task_key: str | None = None,
) -> dict[str, Any]:
    result = request_json(
        "POST",
        f"/api/authV2/open/device/{device_id}/image",
        api_key,
        base_url=base_url,
        body=image_payload(image_path, refresh_now=refresh_now, task_key=task_key),
    )
    if not isinstance(result, dict):
        raise ApiError("推送响应格式无效")
    return result


def push_canvas(
    api_key: str,
    device_id: str,
    payload: dict[str, Any],
    *,
    base_url: str = DEFAULT_BASE_URL,
) -> dict[str, Any]:
    result = request_json(
        "POST",
        f"/api/authV2/open/device/{device_id}/canvas",
        api_key,
        base_url=base_url,
        body=payload,
    )
    if not isinstance(result, dict):
        raise ApiError("Canvas 推送响应格式无效")
    return result
