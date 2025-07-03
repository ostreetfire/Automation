from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import get_current_utc, safe_slugify, calculate_sha256


def test_get_current_utc_timezone() -> None:
    ts = get_current_utc()
    assert ts.tzinfo is timezone.utc
    now = datetime.now(timezone.utc)
    assert abs((now - ts).total_seconds()) < 2


def test_safe_slugify() -> None:
    assert safe_slugify("Hello, World!") == "hello-world"
    assert safe_slugify(" Multiple   spaces ") == "multiple-spaces"
    assert safe_slugify("special__chars!*&") == "special-chars"


def test_calculate_sha256(tmp_path: Path) -> None:
    file_path = tmp_path / "test.txt"
    data = b"sample data"
    file_path.write_bytes(data)
    expected = hashlib.sha256(data).hexdigest()
    assert calculate_sha256(file_path) == expected
