from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx

from app.services.llm_cache import LLMCache


class LLMConfigurationError(RuntimeError):
    """Raised when required LLM settings are missing or invalid."""


class LLMServiceError(RuntimeError):
    """Raised when the LLM provider request fails."""


class DeepSeekClient:
    def __init__(self) -> None:
        self.api_key = _clean_env_value(os.getenv("DEEPSEEK_API_KEY", ""))
        self.base_url = _clean_env_value(os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")).rstrip("/")
        self.model = _clean_env_value(os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
        self.cache = LLMCache()

    def _ensure_configured(self) -> None:
        if not self.api_key:
            raise LLMConfigurationError("DEEPSEEK_API_KEY is not set.")
        for name, value in {
            "DEEPSEEK_API_KEY": self.api_key,
            "DEEPSEEK_BASE_URL": self.base_url,
            "DEEPSEEK_MODEL": self.model,
        }.items():
            try:
                value.encode("ascii")
            except UnicodeEncodeError as exc:
                raise LLMConfigurationError(
                    f"{name} contains non-ASCII characters. "
                    "Set the real DeepSeek value, not placeholder text."
                ) from exc

    async def chat_text(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        self._ensure_configured()
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/chat/completions"
        cache_key = self.cache.build_key(
            provider="deepseek",
            model=self.model,
            base_url=self.base_url,
            messages=messages,
            temperature=temperature,
        )
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            async with httpx.AsyncClient(timeout=45, trust_env=False) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPStatusError as exc:
            raise LLMServiceError(f"LLM API returned HTTP {exc.response.status_code}: {exc.response.text}") from exc
        except httpx.HTTPError as exc:
            raise LLMServiceError(f"LLM API request failed: {exc}") from exc

        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMServiceError(f"LLM API response shape is invalid: {body}") from exc
        self.cache.set(
            cache_key,
            content,
            {
                "provider": "deepseek",
                "model": self.model,
                "base_url": self.base_url,
                "temperature": temperature,
            },
        )
        return content

    async def chat_json(self, messages: list[dict[str, str]], temperature: float = 0.1) -> dict[str, Any]:
        text = await self.chat_text(messages, temperature=temperature)
        return extract_json_object(text)


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        value = json.loads(stripped)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise LLMServiceError("LLM did not return a parseable JSON object.")
    try:
        value = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        preview = text.strip().replace("\n", " ")[:300]
        raise LLMServiceError(f"LLM returned invalid JSON. Preview: {preview}") from exc
    if not isinstance(value, dict):
        raise LLMServiceError("LLM JSON response is not an object.")
    return value


def _clean_env_value(value: str) -> str:
    return value.strip().strip('"').strip("'")
