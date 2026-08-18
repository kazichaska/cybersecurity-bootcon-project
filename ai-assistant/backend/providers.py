"""LLM provider abstraction.

Both providers speak the OpenAI chat-completions schema, so swapping the
backend in production is a config change (AI_PROVIDER + OPENAI_API_KEY),
not a code change.
"""

import os
from abc import ABC, abstractmethod

import requests


class ProviderError(RuntimeError):
    pass


class Provider(ABC):
    @abstractmethod
    def chat(self, messages: list[dict[str, str]]) -> str:
        """Send a chat-completions style message list, return the reply text."""


class OllamaProvider(Provider):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(self, messages: list[dict[str, str]]) -> str:
        try:
            resp = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={"model": self.model, "messages": messages, "stream": False},
                timeout=120,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise ProviderError(f"Ollama request failed: {exc}") from exc
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ProviderError(f"Unexpected Ollama response shape: {data}") from exc


class OpenAIProvider(Provider):
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ProviderError(
                "AI_PROVIDER=openai but OPENAI_API_KEY is not set. "
                "Set it in ai-assistant/.env before switching providers."
            )
        self.api_key = api_key
        self.model = model

    def chat(self, messages: list[dict[str, str]]) -> str:
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": messages},
                timeout=120,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise ProviderError(f"OpenAI request failed: {exc}") from exc
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ProviderError(f"Unexpected OpenAI response shape: {data}") from exc


def get_provider() -> Provider:
    kind = os.environ.get("AI_PROVIDER", "ollama").strip().lower()
    if kind == "ollama":
        return OllamaProvider(
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434"),
            model=os.environ.get("OLLAMA_MODEL", "qwen2.5:0.5b"),
        )
    if kind == "openai":
        return OpenAIProvider(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        )
    raise ProviderError(f"Unknown AI_PROVIDER: {kind!r} (expected 'ollama' or 'openai')")
