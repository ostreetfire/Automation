from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import re
from pathlib import Path

__all__ = [
    "get_current_utc",
    "safe_slugify",
    "calculate_sha256",
]

_slug_pattern = re.compile(r"[^a-zA-Z0-9]+")


def get_current_utc() -> datetime:
    """Return the current UTC time as an aware ``datetime`` object."""
    return datetime.now(timezone.utc)


def safe_slugify(value: str) -> str:
    """Return a filesystem and URL safe slug representation of ``value``."""
    value = value.strip().lower()
    value = _slug_pattern.sub("-", value)
    return value.strip("-")


def calculate_sha256(path: Path) -> str:
    """Return the hexadecimal SHA-256 digest of the file at ``path``."""
    hash_obj = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()
