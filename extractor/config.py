from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-5.4"
DEFAULT_REASONING_EFFORT = "high"


@dataclass(frozen=True)
class ApiConfig:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    organization: Optional[str] = None
    project: Optional[str] = None
    model: str = DEFAULT_MODEL
    reasoning_effort: str = DEFAULT_REASONING_EFFORT
    timeout_seconds: int = 300
    max_retries: int = 4
    delete_remote_file_after_run: bool = False


@dataclass(frozen=True)
class AppConfig:
    pdf_dir: Path
    api_file: Path
    out_dir: Path
    model: Optional[str] = None
    reasoning_effort: Optional[str] = None
    max_pdfs: Optional[int] = None
    overwrite: bool = False
    keep_remote_files: bool = False
    verbose: bool = True

    @property
    def effective_model(self) -> Optional[str]:
        return self.model

    @property
    def effective_reasoning_effort(self) -> Optional[str]:
        return self.reasoning_effort


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_").replace(" ", "_")


def _parse_env_like_text(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[_normalize_key(key)] = _strip_quotes(value)
    return result


def _load_raw_api_file(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"API config file is empty: {path}")

    if text.startswith("{"):
        data = json.loads(text)
        return {_normalize_key(k): v for k, v in data.items()}

    parsed = _parse_env_like_text(text)
    if parsed:
        return parsed

    # Plain key-only file
    return {"openai_api_key": text}


def load_api_config(
    path: Path,
    *,
    model_override: Optional[str] = None,
    reasoning_override: Optional[str] = None,
    keep_remote_files: bool = False,
) -> ApiConfig:
    if not path.exists():
        raise FileNotFoundError(f"API config file not found: {path}")

    data = _load_raw_api_file(path)

    api_key = (
        data.get("openai_api_key")
        or data.get("api_key")
        or data.get("key")
        or os.getenv("OPENAI_API_KEY")
    )
    if not api_key:
        raise ValueError(
            "Could not find an API key. Put OPENAI_API_KEY=<your_key> in gpt_api.txt or export OPENAI_API_KEY."
        )

    base_url = (
        data.get("openai_base_url")
        or data.get("base_url")
        or os.getenv("OPENAI_BASE_URL")
        or DEFAULT_BASE_URL
    )
    organization = data.get("openai_organization") or data.get("organization") or os.getenv("OPENAI_ORGANIZATION")
    project = data.get("openai_project") or data.get("project") or os.getenv("OPENAI_PROJECT")
    model = model_override or data.get("model") or os.getenv("OPENAI_MODEL") or DEFAULT_MODEL
    reasoning_effort = (
        reasoning_override
        or data.get("reasoning_effort")
        or os.getenv("OPENAI_REASONING_EFFORT")
        or DEFAULT_REASONING_EFFORT
    )
    timeout_seconds = int(data.get("timeout_seconds") or os.getenv("OPENAI_TIMEOUT_SECONDS") or 300)
    max_retries = int(data.get("max_retries") or os.getenv("OPENAI_MAX_RETRIES") or 4)
    delete_remote_file_after_run = (
        str(data.get("delete_remote_file_after_run") or os.getenv("DELETE_REMOTE_FILE_AFTER_RUN") or "false")
        .strip()
        .lower()
        in {"1", "true", "yes", "y"}
    )
    if keep_remote_files:
        delete_remote_file_after_run = False

    return ApiConfig(
        api_key=api_key,
        base_url=base_url,
        organization=organization,
        project=project,
        model=model,
        reasoning_effort=reasoning_effort,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        delete_remote_file_after_run=delete_remote_file_after_run,
    )