"""Local LLM backend clients and utilities."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Protocol

from .config import GenerationConfig


class LLMBackend(Protocol):
    """Protocol for model backends used by agents."""

    def generate(self, *, model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Generate a completion for an agent prompt."""


@dataclass
class OllamaBackend:
    """Simple Ollama chat backend."""

    config: GenerationConfig

    def generate(self, *, model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
        payload: Dict[str, Any] = {
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "options": {
                "temperature": temperature,
                "top_p": self.config.top_p,
            },
        }

        last_exc: Exception | None = None
        for attempt in range(self.config.retry_attempts + 1):
            try:
                request = urllib.request.Request(
                    url=f"{self.config.ollama_url}/api/chat",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                    status_code = getattr(response, "status", 200)
                    if status_code >= 400:
                        raise RuntimeError(f"Ollama request failed with status {status_code}.")
                    body = json.loads(response.read().decode("utf-8"))
                message = body.get("message", {}).get("content", "").strip()
                if not message:
                    raise ValueError("Ollama returned an empty response.")
                return message
            except (urllib.error.URLError, urllib.error.HTTPError, ValueError, RuntimeError) as exc:
                last_exc = exc
                if attempt >= self.config.retry_attempts:
                    break
                time.sleep(1.2 * (attempt + 1))

        raise RuntimeError(f"Ollama generation failed after retries: {last_exc}")
