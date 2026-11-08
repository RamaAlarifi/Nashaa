"""OpenAI assessment provider (Chat Completions REST API, structured JSON output).

Reuses the Gemini module's prompt, evidence rules and JSON parsing so both
providers produce the same assessment shape. All failures raise an
:class:`AIServiceError` subclass so callers keep the previous result.
"""

from __future__ import annotations

import json
import re
from typing import Any, Iterable

import httpx

from app.ai.base import (
    AIConfigurationError,
    AIQuotaError,
    AIResponseError,
    AIServiceError,
    AITimeoutError,
    AIUnavailableError,
    AssessmentInput,
    AssessmentProvider,
    AssessmentResult,
)
from app.ai.gemini import REQUIRED_KEYS, SOURCE_DISCLOSURE, SYSTEM_INSTRUCTION, _build_prompt, _parse_json_content
from app.config import get_settings

OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"


class OpenAIAssessmentProvider(AssessmentProvider):
    name = "openai"

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: float | None = None) -> None:
        settings = get_settings()
        self._api_key = (api_key if api_key is not None else settings.openai_api_key).strip()
        self._model = (model or settings.openai_model).strip()
        self._timeout = timeout if timeout is not None else settings.ai_timeout_seconds
        if not re.fullmatch(r"[A-Za-z0-9._:-]+", self._model):
            raise AIConfigurationError("An available OpenAI model must be configured (OPENAI_MODEL).")
        if not self._api_key:
            raise AIConfigurationError("OpenAI API key is not configured (OPENAI_API_KEY).")

    def complete_json(self, system: str, user: str, fields: Iterable[str], max_tokens: int) -> dict:
        """Send one structured-output request and return the parsed JSON object."""
        fields = list(fields)
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_schema", "json_schema": {"name": "nashaa_result", "strict": True, "schema": {
                "type": "object", "properties": {key: {"type": "string"} for key in fields},
                "required": fields, "additionalProperties": False,
            }}},
            # Includes reasoning tokens on reasoning models, so keep it generous.
            "max_completion_tokens": max_tokens,
        }
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(OPENAI_ENDPOINT, headers={"Authorization": f"Bearer {self._api_key}"}, json=payload)
        except httpx.TimeoutException as exc:
            raise AITimeoutError("The AI service took too long to respond.") from exc
        except httpx.HTTPError as exc:
            raise AIServiceError("Could not reach the AI service.") from exc

        if response.status_code != 200:
            if response.status_code in (500, 502, 503, 504):
                raise AIUnavailableError("The AI service is temporarily unavailable.")
            if response.status_code == 429:
                raise AIQuotaError("OpenAI generation quota is unavailable.")
            raise AIServiceError(f"AI service returned HTTP {response.status_code}. This may be a quota, key, or model issue.")

        try:
            body = response.json()
            choice = body["choices"][0]
            message = choice["message"]
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            raise AIResponseError("The AI service did not return a usable response.") from exc
        if choice.get("finish_reason") != "stop" or message.get("refusal"):
            raise AIResponseError("The AI response was blocked or incomplete. Please try again.")
        text = message.get("content")
        if not isinstance(text, str) or not text.strip():
            raise AIResponseError("AI response contained no text content.")
        return _parse_json_content(text)

    def generate(self, data: AssessmentInput) -> AssessmentResult:
        mapping = self.complete_json(SYSTEM_INSTRUCTION, _build_prompt(data), [*REQUIRED_KEYS, "sources"], 16000)
        # Source provenance is set by the application, not an unverifiable model claim.
        mapping["sources"] = SOURCE_DISCLOSURE
        return AssessmentResult.from_mapping(mapping)
