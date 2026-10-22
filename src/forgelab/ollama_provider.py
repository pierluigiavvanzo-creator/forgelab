from __future__ import annotations

import json
import math
import socket
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .model_router import (
    ProviderPermanentError,
    ProviderResponse,
    ProviderTransientError,
)


# Context sizing (2026-10-22). A fixed num_ctx=4096 let Ollama silently
# drop the middle of 4,475/4,815-token review prompts (llama_server.go
# context shift keeps only 2,050 tokens). The context is now sized from
# the prompt instead, and ForgeLab fails closed rather than accept a
# truncated prompt.
MIN_NUM_CTX = 4096
MAX_NUM_CTX = 16384
NUM_CTX_STEP = 1024
NUM_PREDICT = 2048
# Observed: ~4.5 chars/token (qwen2.5-coder) and ~3.8 (gemma4) on the
# synthetic review prompts. 3.5 over-estimates tokens on purpose.
CONSERVATIVE_CHARS_PER_TOKEN = 3.5
CONTEXT_MARGIN_TOKENS = 64
# A complete prompt never approaches 8 chars/token; a higher ratio means
# the server evaluated only part of the prompt.
TRUNCATION_CHARS_PER_TOKEN = 8.0


def required_num_ctx(
    prompt: str,
    response_format: dict[str, object] | str | None = None,
) -> int:
    """Context needed for the whole prompt plus the bounded output."""

    schema_chars = (
        len(json.dumps(response_format))
        if isinstance(response_format, dict)
        else 0
    )
    estimated_prompt_tokens = math.ceil(
        (len(prompt) + schema_chars)
        / CONSERVATIVE_CHARS_PER_TOKEN
    )
    needed = (
        estimated_prompt_tokens
        + NUM_PREDICT
        + CONTEXT_MARGIN_TOKENS
    )
    needed = math.ceil(needed / NUM_CTX_STEP) * NUM_CTX_STEP

    if needed > MAX_NUM_CTX:
        raise ProviderPermanentError(
            "Prompt needs about "
            f"{needed} tokens of context, above the bounded local "
            f"maximum {MAX_NUM_CTX}; refusing to send it because "
            "Ollama would silently truncate it"
        )

    return max(MIN_NUM_CTX, needed)


def _check_prompt_not_truncated(
    prompt: str,
    result: dict[str, object],
) -> None:
    evaluated = int(result.get("prompt_eval_count") or 0) + int(
        result.get("prompt_eval_cached_count") or 0
    )

    if (
        evaluated > 0
        and len(prompt) / evaluated > TRUNCATION_CHARS_PER_TOKEN
    ):
        raise ProviderPermanentError(
            "Ollama evaluated only "
            f"{evaluated} prompt tokens for a {len(prompt)}-character "
            "prompt; the prompt was probably truncated, so the "
            "response is rejected"
        )


class OllamaProvider:
    """Loopback-only Ollama provider for ForgeLab."""

    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:11434",
    ) -> None:
        endpoint = endpoint.rstrip("/")
        parsed = urlparse(endpoint)

        if (
            parsed.scheme != "http"
            or parsed.hostname not in {
                "127.0.0.1",
                "localhost",
                "::1",
            }
        ):
            raise ValueError(
                "Ollama endpoint must be loopback-only HTTP"
            )

        self.endpoint = endpoint

    def reset_after_repeat_limit(
        self,
        model: str,
        timeout_seconds: int,
    ) -> None:
        """Unload the local model before the existing bounded retry."""

        payload = json.dumps({
            "model": model,
            "prompt": "",
            "stream": False,
            "keep_alive": 0,
        }).encode("utf-8")

        request = Request(
            f"{self.endpoint}/api/generate",
            data=payload,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=timeout_seconds,
            ) as response:
                raw = response.read()

        except HTTPError as error:
            try:
                detail = error.read().decode(
                    "utf-8",
                    errors="replace",
                )
            except Exception:
                detail = str(error)

            if error.code >= 500:
                raise ProviderTransientError(
                    "Ollama repeat-limit reset failed "
                    f"with HTTP {error.code}: {detail}"
                ) from error

            raise ProviderPermanentError(
                "Ollama repeat-limit reset failed "
                f"with HTTP {error.code}: {detail}"
            ) from error

        except (
            URLError,
            TimeoutError,
            socket.timeout,
            ConnectionError,
        ) as error:
            raise ProviderTransientError(
                "Ollama repeat-limit reset unavailable: "
                f"{error}"
            ) from error

        try:
            result = json.loads(
                raw.decode("utf-8")
            )
        except Exception as error:
            raise ProviderPermanentError(
                "Ollama repeat-limit reset returned invalid JSON"
            ) from error

        if not isinstance(result, dict):
            raise ProviderPermanentError(
                "Ollama repeat-limit reset response "
                "is not an object"
            )

        if result.get("error"):
            raise ProviderPermanentError(
                "Ollama repeat-limit reset failed: "
                + str(result["error"])
            )

    def invoke(
        self,
        model: str,
        prompt: str,
        timeout_seconds: int,
        response_format: dict[str, object] | str | None = None,
    ) -> ProviderResponse:

        request_payload: dict[str, object] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": required_num_ctx(
                    prompt,
                    response_format,
                ),
                # Bounded but large enough for structured
                # multi-file AI Developer JSON patches.
                "num_predict": NUM_PREDICT,
            },
        }

        if response_format is not None:
            request_payload["format"] = response_format

        payload = json.dumps(
            request_payload
        ).encode("utf-8")

        request = Request(
            f"{self.endpoint}/api/generate",
            data=payload,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=timeout_seconds,
            ) as response:
                raw = response.read()

        except HTTPError as error:
            try:
                detail = error.read().decode(
                    "utf-8",
                    errors="replace",
                )
            except Exception:
                detail = str(error)

            if error.code >= 500:
                raise ProviderTransientError(
                    f"Ollama HTTP {error.code}: {detail}"
                ) from error

            raise ProviderPermanentError(
                f"Ollama HTTP {error.code}: {detail}"
            ) from error

        except (
            URLError,
            TimeoutError,
            socket.timeout,
            ConnectionError,
        ) as error:
            raise ProviderTransientError(
                f"Ollama unavailable: {error}"
            ) from error

        try:
            result = json.loads(
                raw.decode("utf-8")
            )
        except Exception as error:
            raise ProviderPermanentError(
                "Ollama returned invalid JSON"
            ) from error

        if not isinstance(result, dict):
            raise ProviderPermanentError(
                "Ollama response is not an object"
            )

        if result.get("error"):
            raise ProviderPermanentError(
                str(result["error"])
            )

        text = result.get("response")

        if not isinstance(text, str):
            raise ProviderPermanentError(
                "Ollama response contains no text"
            )

        _check_prompt_not_truncated(prompt, result)

        return ProviderResponse(
            text=text,
            input_tokens=int(
                result.get(
                    "prompt_eval_count",
                    0,
                )
            ),
            output_tokens=int(
                result.get(
                    "eval_count",
                    0,
                )
            ),
            actual_cost=Decimal("0"),
            cache_read_tokens=0,
        )
