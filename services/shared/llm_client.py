"""
Shared LLM client — wraps Groq for all SDLC agents.
Single place to swap models, change defaults, or add tracing.
"""
import os
from typing import Optional, List, Dict
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Default model — Groq's Llama 3.3 70B is fast + capable for code/design tasks.
DEFAULT_MODEL = os.getenv("NEURA_LLM_MODEL", "llama-3.3-70b-versatile")
DEFAULT_TEMPERATURE = float(os.getenv("NEURA_LLM_TEMPERATURE", "0.2"))


class NeuraLLM:
    """Thin wrapper around Groq for consistent agent behavior."""

    def __init__(self, model: Optional[str] = None, temperature: Optional[float] = None):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY missing — set it in .env")
        self.client = Groq(api_key=api_key)
        self.model = model or DEFAULT_MODEL
        self.temperature = temperature if temperature is not None else DEFAULT_TEMPERATURE

    def chat(
        self,
        system: str,
        user: str,
        history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 4096,
    ) -> str:
        """Single-turn or multi-turn chat. Returns the assistant text."""
        messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user})

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""

    def json_chat(self, system: str, user: str, max_tokens: int = 4096) -> str:
        """
        Force JSON-mode output. Use this for structured tasks (design docs,
        test plans, etc.) where the agent must return parseable JSON.
        """
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=self.temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content or "{}"
