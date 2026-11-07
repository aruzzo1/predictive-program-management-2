"""LLM provider selection for the agentic layer.

A real provider is used only when it is actually configured: the `openai` package is installed AND
OPENAI_API_KEY is set. Then the agents run in REAL_LLM_MODE through the OpenAI Responses API with
structured output (the SDK's `responses.parse` with a Pydantic `text_format`). Otherwise they run in
MOCK_AGENT_MODE: deterministic, rule-based stand-ins for the generator and critic that exercise the
full architecture without any model call. Mock output must never be presented as LLM reasoning.

Structured output only guarantees the *shape* of a response. Everything the model returns is still
re-validated in Python (agents.validation) and the critic total is always computed in Python.

Errors:
  LLMConfigurationError: the request cannot succeed as configured (bad key, unknown model, unsupported
    parameter, no quota). Fatal: the episode stops rather than producing a trace of failed calls.
  LLMCallError: this one call failed (timeout, connection, rate limit or server error after the SDK's
    retries, refusal, truncated or unparseable output). The agent records it and the search continues.
Error messages are redacted so that no key material ever reaches a trace or log.
"""

from __future__ import annotations

import importlib.util
import re
import time
from typing import Protocol, TypeVar

from pydantic import BaseModel

from ppm_agent.config import get_settings

MOCK_AGENT_MODE = "MOCK_AGENT_MODE"
REAL_LLM_MODE = "REAL_LLM_MODE"

T = TypeVar("T", bound=BaseModel)


class LLMCallError(RuntimeError):
    """One model call failed; recoverable at the level of the search."""


class LLMConfigurationError(RuntimeError):
    """The provider is misconfigured; no call can succeed."""


class LLMClient(Protocol):
    mode: str
    model: str

    def complete(self, system: str, user: str, schema: type[T]) -> T:
        """Return the model's response parsed into `schema`; raise LLMCallError / LLMConfigurationError."""


def redact(text: str) -> str:
    """Remove anything that looks like an API key (including masked fragments) from an error message."""
    return re.sub(r"sk-[A-Za-z0-9_\-*]+", "sk-[REDACTED]", str(text))


class OpenAIResponsesClient:
    """OpenAI Responses API adapter: temperature 0, strict structured output, responses not stored."""

    mode = REAL_LLM_MODE
    provider = "openai-responses"

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini", client=None, timeout: float = 90.0,
                 max_retries: int = 2):
        if client is None:
            from openai import OpenAI

            client = OpenAI(api_key=api_key, timeout=timeout, max_retries=max_retries)
        self._client, self.model = client, model
        self.calls: list[dict] = []  # per-call usage and latency (no prompt or key content)

    def complete(self, system: str, user: str, schema: type[T]) -> T:
        import openai

        start = time.time()
        try:
            response = self._client.responses.parse(model=self.model, instructions=system, input=user, text_format=schema,
                                                    temperature=0, store=False)
        except (openai.AuthenticationError, openai.PermissionDeniedError, openai.NotFoundError, openai.BadRequestError) as exc:
            raise LLMConfigurationError(f"{type(exc).__name__}: {redact(exc)}") from None
        except openai.RateLimitError as exc:
            if getattr(exc, "code", None) == "insufficient_quota":
                raise LLMConfigurationError(f"insufficient_quota: {redact(exc)}") from None
            raise LLMCallError(f"RateLimitError: {redact(exc)}") from None
        except openai.OpenAIError as exc:  # timeouts, connection errors, 5xx, parse/validation failures in the SDK
            raise LLMCallError(f"{type(exc).__name__}: {redact(exc)}") from None
        except ValueError as exc:  # pydantic ValidationError on a malformed structured response
            raise LLMCallError(f"structured output did not match {schema.__name__}: {redact(exc)}") from None

        usage = getattr(response, "usage", None)
        self.calls.append({"schema": schema.__name__, "seconds": round(time.time() - start, 2), "status": getattr(response, "status", None),
                           "input_tokens": getattr(usage, "input_tokens", None), "output_tokens": getattr(usage, "output_tokens", None)})
        if getattr(response, "status", "completed") == "incomplete":
            reason = getattr(getattr(response, "incomplete_details", None), "reason", None)
            raise LLMCallError(f"incomplete response ({reason})")
        parsed = getattr(response, "output_parsed", None)
        if parsed is None:
            raise LLMCallError(f"no structured output (refusal: {redact(refusal_text(response)) or 'none'})")
        return parsed

    def usage_summary(self) -> dict:
        total = lambda key: sum(c[key] or 0 for c in self.calls)  # noqa: E731
        return {"provider": self.provider, "model": self.model, "successful_responses": len(self.calls),
                "input_tokens": total("input_tokens"), "output_tokens": total("output_tokens")}


def refusal_text(response) -> str:
    for item in getattr(response, "output", None) or []:
        for part in getattr(item, "content", None) or []:
            if getattr(part, "type", None) == "refusal":
                return getattr(part, "refusal", "") or ""
    return ""


def detect_llm_client() -> LLMClient | None:
    """A configured real client, or None (=> MOCK_AGENT_MODE). The key is passed to the SDK, never printed."""
    settings = get_settings()
    if settings.openai_api_key and importlib.util.find_spec("openai") is not None:
        return OpenAIResponsesClient(settings.openai_api_key, settings.openai_model)
    return None


def agent_mode(client: LLMClient | None) -> str:
    return client.mode if client is not None else MOCK_AGENT_MODE
