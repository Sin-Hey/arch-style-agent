from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx


class LLMConfigurationError(RuntimeError):
    """Raised when required LLM settings are missing."""


class LLMServiceError(RuntimeError):
    """Raised when the LLM provider request fails."""


class DeepSeekClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    def _ensure_configured(self) -> None:
        if not self.api_key:
            raise LLMConfigurationError(
                "未配置 DEEPSEEK_API_KEY。请先设置环境变量 DEEPSEEK_API_KEY，再重试接口调用。"
            )

    async def chat_text(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        self._ensure_configured()
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=45) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPStatusError as exc:
            raise LLMServiceError(f"LLM API 返回错误：{exc.response.status_code} {exc.response.text}") from exc
        except httpx.HTTPError as exc:
            raise LLMServiceError(f"LLM API 请求失败：{exc}") from exc

        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMServiceError(f"LLM API 响应格式异常：{body}") from exc

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
        raise LLMServiceError("LLM 未返回可解析的 JSON 对象。")
    value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise LLMServiceError("LLM JSON 响应不是对象。")
    return value
