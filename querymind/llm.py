"""Minimal chat-completion client for any OpenAI-compatible API (Groq by default)."""

import os
from typing import Protocol


class LLM(Protocol):
    def chat(self, messages: list[dict]) -> str: ...


PROVIDERS = {
    # name: (base_url, api-key env var, default model)
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY", "openai/gpt-oss-120b"),
    "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY", "gpt-4o-mini"),
}


class OpenAICompatibleLLM:
    def __init__(self, provider: str | None = None, model: str | None = None, temperature: float = 0.0):
        from openai import OpenAI

        provider = provider or os.getenv("LLM_PROVIDER") or (
            "groq" if os.getenv("GROQ_API_KEY") else "openai"
        )
        base_url, key_env, default_model = PROVIDERS[provider]
        api_key = os.getenv(key_env)
        if not api_key:
            raise RuntimeError(f"No API key found: set GROQ_API_KEY or OPENAI_API_KEY (looked for {key_env})")
        # free tiers rate-limit a lot; the SDK backs off on 429s
        self.client = OpenAI(base_url=base_url, api_key=api_key, max_retries=10)
        self.model = model or os.getenv("LLM_MODEL") or default_model
        self.temperature = temperature

    def chat(self, messages: list[dict]) -> str:
        resp = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=self.temperature
        )
        return resp.choices[0].message.content or ""
