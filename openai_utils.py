"""Utility helpers for interacting with OpenAI's API."""

import logging
import os
import time
from pathlib import Path
from typing import List

import yaml
from openai import OpenAI

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).resolve().parent / "config" / "settings.yaml"


def _load_settings() -> dict:
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.warning("Config file not found: %s", CONFIG_FILE)
        return {}


settings = _load_settings()
client = OpenAI(api_key=settings.get("openai_api_key") or os.getenv("OPENAI_API_KEY"))


def ask_openai(system_prompt: str, user_prompt: str) -> str:
    """Request a chat completion and return the assistant's reply."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    start_time = time.perf_counter()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
        tool_choice="none",
    )
    elapsed = time.perf_counter() - start_time
    usage = response.usage
    logger.info(
        "OpenAI tokens used: prompt=%s completion=%s (%.2fs)",
        usage.prompt_tokens,
        usage.completion_tokens,
        elapsed,
    )
    return response.choices[0].message.content


def embed_text(text: str) -> List[float]:
    """Return an embedding for the provided text."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


__all__ = ["ask_openai", "embed_text", "client"]
