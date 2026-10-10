from __future__ import annotations

import json

from .model_router import (
    ProviderPermanentError,
    ProviderResponse,
    ProviderTransientError,
)

# Constraints ForgeLab's deterministic validators enforce after the call.
# They are removed from the transport schema so structured output accepts it.
_VALIDATOR_ONLY_KEYWORDS = frozenset({
    "minLength",
    "maxLength",
    "minItems",
    "maxItems",
    "minimum",
    "maximum",
    "pattern",
    "uniqueItems",
})

_MAX_OUTPUT_TOKENS = 16000


def _transport_schema(schema: object) -> object:
    if isinstance(schema, dict):
        return {
            key: _transport_schema(value)
            for key, value in schema.items()
            if key not in _VALIDATOR_ONLY_KEYWORDS
        }
    if isinstance(schema, list):
        return [_transport_schema(item) for item in schema]
    return schema


class AnthropicProvider:
    """Remote Claude provider for ForgeLab. No local model memory is used.

    Credentials are resolved by the official SDK from the process
    environment (ANTHROPIC_API_KEY); ForgeLab never stores or logs them.
    Cost is not returned here: the router prices each call from the route's
    configured pricing and enforces max_call_cost and the run budget.
    """

    def __init__(self, sdk: object | None = None) -> None:
        # The SDK module is injectable so tests run without the dependency.
        self._sdk = sdk
        self._client: object | None = None

    def _resolve_sdk(self) -> object:
        if self._sdk is None:
            try:
                import anthropic
            except ImportError as error:
                raise ProviderPermanentError(
                    "Anthropic SDK is not installed: run "
                    "'py -3.11 -m pip install anthropic'"
                ) from error
            self._sdk = anthropic
        return self._sdk

    def _resolve_client(self) -> object:
        if self._client is None:
            # ForgeLab's router owns retries and their accounting.
            self._client = self._resolve_sdk().Anthropic(  # type: ignore[attr-defined]
                max_retries=0,
            )
        return self._client

    def invoke(
        self,
        model: str,
        prompt: str,
        timeout_seconds: int,
        response_format: dict[str, object] | str | None = None,
    ) -> ProviderResponse:
        anthropic = self._resolve_sdk()
        client = self._resolve_client()
        request: dict[str, object] = {
            "model": model,
            "max_tokens": _MAX_OUTPUT_TOKENS,
            "messages": [{"role": "user", "content": prompt}],
        }
        if isinstance(response_format, dict):
            request["output_config"] = {
                "format": {
                    "type": "json_schema",
                    "schema": _transport_schema(response_format),
                }
            }
        elif response_format is not None:
            request["messages"] = [{
                "role": "user",
                "content": (
                    prompt.rstrip()
                    + "\n\nReturn exactly one JSON value and nothing else."
                ),
            }]

        try:
            response = client.with_options(  # type: ignore[attr-defined]
                timeout=float(timeout_seconds),
            ).messages.create(**request)
        except anthropic.RateLimitError as error:
            raise ProviderTransientError(
                f"Anthropic rate limit: {error}"
            ) from error
        except anthropic.APIConnectionError as error:
            raise ProviderTransientError(
                f"Anthropic unavailable: {error}"
            ) from error
        except anthropic.APIStatusError as error:
            if error.status_code >= 500:
                raise ProviderTransientError(
                    f"Anthropic HTTP {error.status_code}: {error}"
                ) from error
            raise ProviderPermanentError(
                f"Anthropic HTTP {error.status_code}: {error}"
            ) from error

        if response.stop_reason == "refusal":
            raise ProviderPermanentError(
                "Anthropic declined the request (stop_reason=refusal)"
            )
        if response.stop_reason == "max_tokens":
            raise ProviderPermanentError(
                "Anthropic response was truncated at max_tokens"
            )

        text = "".join(
            block.text
            for block in response.content
            if block.type == "text"
        )
        if not text.strip():
            raise ProviderPermanentError(
                "Anthropic response contains no text"
            )
        if isinstance(response_format, dict):
            try:
                json.loads(text)
            except ValueError as error:
                raise ProviderPermanentError(
                    "Anthropic returned invalid JSON"
                ) from error

        usage = response.usage
        cache_read = int(
            getattr(usage, "cache_read_input_tokens", 0) or 0
        )
        cache_write = int(
            getattr(usage, "cache_creation_input_tokens", 0) or 0
        )
        return ProviderResponse(
            text=text,
            # Priced conservatively: every input token at the full rate.
            input_tokens=int(usage.input_tokens) + cache_read + cache_write,
            output_tokens=int(usage.output_tokens),
            actual_cost=None,
            cache_read_tokens=cache_read,
        )
