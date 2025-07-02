from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from uuid import uuid4


def compute_sha256(file_path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    hash_obj = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def build_metadata(upload_path: Path, case_id: str, file_hash: str, file_uuid: str) -> Dict[str, str]:
    """Create metadata dictionary for a stored file."""
    return {
        "case_id": case_id,
        "uuid": file_uuid,
        "hash": file_hash,
        "original_filename": upload_path.name,
    }


def store_file(upload_path: Path, case_id: str, storage_root: Path = Path("storage/raw_files")) -> Dict[str, Any]:
    """Move uploaded file to structured storage and write metadata sidecar."""
    file_hash = compute_sha256(upload_path)
    file_uuid = uuid4().hex

    now = datetime.utcnow()
    destination_dir = storage_root / str(case_id) / f"{now.year:04d}" / f"{now.month:02d}"
    destination_dir.mkdir(parents=True, exist_ok=True)

    destination_path = destination_dir / f"{file_uuid}{upload_path.suffix}"
    upload_path.rename(destination_path)

    metadata = build_metadata(upload_path, case_id, file_hash, file_uuid)
    metadata["stored_path"] = str(destination_path)

    metadata_path = destination_path.with_suffix(destination_path.suffix + ".json")
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return {"path": str(destination_path), "metadata": metadata}


__all__ = [
    "compute_sha256",
    "build_metadata",
    "store_file",
]
