from __future__ import annotations

import json
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
        return self._invoke(
            model,
            prompt,
            timeout_seconds,
            response_format,
            repeat_limit_recovery=False,
        )

    def invoke_repeat_limit_recovery(
        self,
        model: str,
        prompt: str,
        timeout_seconds: int,
        response_format: dict[str, object] | str | None = None,
    ) -> ProviderResponse:
        """Run the existing retry with explicit anti-repeat sampling."""

        return self._invoke(
            model,
            prompt,
            timeout_seconds,
            response_format,
            repeat_limit_recovery=True,
        )

    def _invoke(
        self,
        model: str,
        prompt: str,
        timeout_seconds: int,
        response_format: dict[str, object] | str | None,
        *,
        repeat_limit_recovery: bool,
    ) -> ProviderResponse:

        options: dict[str, object] = {
            "temperature": 0.1,
            "num_ctx": 4096,
            # Bounded but large enough for structured
            # multi-file AI Developer JSON patches.
            "num_predict": 2048,
        }

        if repeat_limit_recovery:
            options.update({
                "repeat_penalty": 1.1,
                "repeat_last_n": 128,
            })

        request_payload: dict[str, object] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": options,
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
