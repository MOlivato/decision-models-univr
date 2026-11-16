"""Configuration: environment variables and optional YAML config files."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class BackendConfig:
    backend: str = "local"
    base_url: str = "http://localhost:11434/v1"
    model: str = "tev1"
    api_key_env: str | None = None
    timeout: int = 60

    @property
    def api_key(self) -> str | None:
        return os.getenv(self.api_key_env) if self.api_key_env else None

    @property
    def endpoint(self) -> str:
        base = self.base_url.rstrip("/")
        if base.endswith("/v1/systemone"):
            return base
        base = base.removesuffix("/v1")
        return f"{base}/v1/systemone"


def load_config(config_file: str | Path | None = None) -> BackendConfig:
    """Load settings from .env, overridden by an optional YAML config file."""
    load_dotenv(ROOT / ".env")
    data: dict = {}
    if config_file:
        path = Path(config_file)
        if not path.is_absolute():
            path = ROOT / path
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    backend = data.get("backend", os.getenv("DM_BACKEND", "local"))
    if backend == "hosted":
        defaults = {
            "base_url": os.getenv("DM_HOSTED_URL", "https://openrouter.ai/api/v1"),
            "model": os.getenv("DM_HOSTED_MODEL", "inception/mercury-decide"),
            "api_key_env": "DM_API_KEY",
            "timeout": int(os.getenv("DM_TIMEOUT", "30")),
        }
    else:
        defaults = {
            "base_url": os.getenv("DM_LOCAL_URL", "http://localhost:11434/v1"),
            "model": os.getenv("DM_LOCAL_MODEL", "tev1"),
            "api_key_env": None,
            "timeout": int(os.getenv("DM_TIMEOUT", "60")),
        }

    return BackendConfig(
        backend=backend,
        base_url=data.get("base_url", defaults["base_url"]),
        model=data.get("model", defaults["model"]),
        api_key_env=data.get("api_key_env", defaults["api_key_env"]),
        timeout=int(data.get("timeout", defaults["timeout"])),
    )
