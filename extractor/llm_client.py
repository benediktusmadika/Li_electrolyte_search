from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from .config import ApiConfig

LOGGER = logging.getLogger(__name__)


class LLMClientError(RuntimeError):
    """Raised when the OpenAI API call fails or returns invalid structured data."""


@dataclass
class UploadedFile:
    file_id: str
    filename: str


class BaseResponsesClient:
    def __init__(self, api_config: ApiConfig):
        self.api_config = api_config

    def upload_file(self, pdf_path: Path) -> UploadedFile:
        raise NotImplementedError

    def delete_file(self, file_id: str) -> None:
        raise NotImplementedError

    def create_structured_response(
        self,
        *,
        file_id: Optional[str],
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: Dict[str, Any],
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError


class HttpResponsesClient(BaseResponsesClient):
    def __init__(self, api_config: ApiConfig):
        super().__init__(api_config)
        self.base_url = api_config.base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_config.api_key}",
            }
        )
        if api_config.organization:
            self.session.headers["OpenAI-Organization"] = api_config.organization
        if api_config.project:
            self.session.headers["OpenAI-Project"] = api_config.project

    def upload_file(self, pdf_path: Path) -> UploadedFile:
        url = f"{self.base_url}/files"
        with pdf_path.open("rb") as handle:
            files = {"file": (pdf_path.name, handle, "application/pdf")}
            data = {"purpose": "user_data"}
            response = self._request("POST", url, files=files, data=data, timeout=self.api_config.timeout_seconds)
        payload = response.json()
        file_id = payload.get("id")
        if not file_id:
            raise LLMClientError(f"File upload succeeded but no file id was returned: {payload}")
        return UploadedFile(file_id=file_id, filename=pdf_path.name)

    def delete_file(self, file_id: str) -> None:
        url = f"{self.base_url}/files/{file_id}"
        try:
            self._request("DELETE", url, timeout=self.api_config.timeout_seconds)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Failed to delete remote file %s: %s", file_id, exc)

    def create_structured_response(
        self,
        *,
        file_id: Optional[str],
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: Dict[str, Any],
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/responses"
        content = [{"type": "input_text", "text": user_prompt}]
        if file_id:
            content.insert(0, {"type": "input_file", "file_id": file_id})
        payload = {
            "model": model or self.api_config.model,
            "reasoning": {"effort": reasoning_effort or self.api_config.reasoning_effort},
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}],
                },
                {"role": "user", "content": content},
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                }
            },
        }
        response = self._request("POST", url, json=payload, timeout=self.api_config.timeout_seconds)
        data = response.json()
        raw_text = _extract_output_text_from_rest_response(data)
        if not raw_text:
            raise LLMClientError(f"No output text found in response payload: {data}")
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise LLMClientError(f"Model output was not valid JSON: {raw_text}") from exc

    def _request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        last_error: Optional[Exception] = None
        for attempt in range(1, self.api_config.max_retries + 1):
            try:
                response = self.session.request(method, url, **kwargs)
                if response.status_code in {408, 409, 429, 500, 502, 503, 504}:
                    raise LLMClientError(
                        f"Transient API error {response.status_code}: {response.text[:1000]}"
                    )
                response.raise_for_status()
                return response
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt >= self.api_config.max_retries:
                    break
                sleep_seconds = min(2 ** attempt, 20)
                LOGGER.warning(
                    "HTTP request failed on attempt %s/%s. Retrying in %ss. Error: %s",
                    attempt,
                    self.api_config.max_retries,
                    sleep_seconds,
                    exc,
                )
                time.sleep(sleep_seconds)
        raise LLMClientError(f"API request failed after retries: {last_error}")


class SdkResponsesClient(BaseResponsesClient):
    def __init__(self, api_config: ApiConfig):
        super().__init__(api_config)
        from openai import OpenAI  # type: ignore

        self.client = OpenAI(
            api_key=api_config.api_key,
            base_url=api_config.base_url,
            organization=api_config.organization,
            project=api_config.project,
            timeout=api_config.timeout_seconds,
            max_retries=api_config.max_retries,
        )

    def upload_file(self, pdf_path: Path) -> UploadedFile:
        with pdf_path.open("rb") as handle:
            uploaded = self.client.files.create(file=handle, purpose="user_data")
        return UploadedFile(file_id=uploaded.id, filename=pdf_path.name)

    def delete_file(self, file_id: str) -> None:
        try:
            self.client.files.delete(file_id)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Failed to delete remote file %s: %s", file_id, exc)

    def create_structured_response(
        self,
        *,
        file_id: Optional[str],
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: Dict[str, Any],
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
    ) -> Dict[str, Any]:
        content = [{"type": "input_text", "text": user_prompt}]
        if file_id:
            content.insert(0, {"type": "input_file", "file_id": file_id})
        response = self.client.responses.create(
            model=model or self.api_config.model,
            reasoning={"effort": reasoning_effort or self.api_config.reasoning_effort},
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}],
                },
                {"role": "user", "content": content},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                }
            },
        )
        raw_text = getattr(response, "output_text", None) or _extract_output_text_from_sdk_response(response)
        if not raw_text:
            raise LLMClientError(f"No output_text returned by SDK response: {response}")
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise LLMClientError(f"Model output was not valid JSON: {raw_text}") from exc


def _extract_output_text_from_rest_response(payload: Dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct

    chunks = []
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content_item in item.get("content", []):
            if content_item.get("type") == "output_text":
                text = content_item.get("text")
                if isinstance(text, str):
                    chunks.append(text)
    return "".join(chunks).strip()


def _extract_output_text_from_sdk_response(response: Any) -> str:
    output = getattr(response, "output", None)
    if not output:
        return ""
    chunks = []
    for item in output:
        if getattr(item, "type", None) != "message":
            continue
        for content_item in getattr(item, "content", []):
            if getattr(content_item, "type", None) == "output_text":
                text = getattr(content_item, "text", None)
                if isinstance(text, str):
                    chunks.append(text)
    return "".join(chunks).strip()


def build_llm_client(api_config: ApiConfig) -> BaseResponsesClient:
    try:
        import openai  # noqa: F401
        from openai import OpenAI  # type: ignore  # noqa: F401

        LOGGER.info("Using the official OpenAI Python SDK client.")
        return SdkResponsesClient(api_config)
    except Exception:
        LOGGER.info("OpenAI Python SDK not available. Falling back to direct HTTP client.")
        return HttpResponsesClient(api_config)