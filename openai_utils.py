import logging
import time
from pathlib import Path
from typing import List

import yaml
from openai import OpenAI

CONFIG_FILE = Path(__file__).resolve().parent / "config" / "settings.yaml"

with CONFIG_FILE.open("r", encoding="utf-8") as f:
    settings = yaml.safe_load(f)

client = OpenAI(api_key=settings.get("openai_api_key"))


def ask_openai(system_prompt: str, user_prompt: str) -> str:
    """Send a chat completion request and return the assistant message."""
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
    logging.info(
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
