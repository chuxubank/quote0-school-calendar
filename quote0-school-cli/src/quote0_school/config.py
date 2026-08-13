from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from .api import DEFAULT_BASE_URL


CONFIG_PATH = Path.home() / ".config" / "quote0-school" / "config.json"


@dataclass(frozen=True)
class Config:
    api_key: str | None
    device_id: str | None
    base_url: str
    api_key_source: str
    device_id_source: str


def load_config() -> Config:
    stored: dict[str, str] = {}
    if CONFIG_PATH.exists():
        try:
            stored = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            stored = {}

    api_key = os.environ.get("DOT_API_KEY")
    env_device = os.environ.get("DOT_DEVICE_ID")
    device_id = env_device or stored.get("device_id")
    base_url = os.environ.get("DOT_BASE_URL") or stored.get("base_url") or DEFAULT_BASE_URL
    return Config(
        api_key=api_key,
        device_id=device_id,
        base_url=base_url,
        api_key_source="env" if api_key else "missing",
        device_id_source="env" if env_device else ("config" if device_id else "missing"),
    )


def save_device(device_id: str, base_url: str | None = None) -> Path:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"device_id": device_id}
    if base_url and base_url != DEFAULT_BASE_URL:
        payload["base_url"] = base_url
    CONFIG_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        CONFIG_PATH.chmod(0o600)
    except OSError:
        pass
    return CONFIG_PATH
