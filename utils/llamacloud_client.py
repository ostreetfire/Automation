import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import yaml


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://cloud.llamaindex.ai"
CONFIG_PATH = Path("config/settings.yaml")


def _load_settings() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def _save_settings(settings: Dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(settings, f)


def set_api_key(api_key: str) -> None:
    """Persist the API key to the settings file."""
    settings = _load_settings()
    settings["llamacloud_api_key"] = api_key
    _save_settings(settings)


def get_api_key() -> str:
    """Return the LlamaCloud API key from environment or config."""
    key = os.getenv("LLAMA_CLOUD_API_KEY")
    if key:
        return key
    settings = _load_settings()
    key = settings.get("llamacloud_api_key")
    if not key:
        raise RuntimeError("LlamaCloud API key not configured")
    return key


def _request(method: str, endpoint: str, max_retries: int = 3, **kwargs) -> requests.Response:
    url = f"{BASE_URL}{endpoint}"
    backoff = 1
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            logger.warning("Request attempt %s failed: %s", attempt, exc)
            if attempt == max_retries:
                raise
            time.sleep(backoff)
            backoff *= 2
    raise RuntimeError("Unreachable")


def upload_file(file_path: str) -> str:
    """Upload a document to LlamaCloud and return the file ID."""
    api_key = get_api_key()
    headers = {"Authorization": f"Bearer {api_key}"}
    with open(file_path, "rb") as f:
        files = {"file": f}
        resp = _request("POST", "/api/v1/files/upload", headers=headers, files=files)
    data = resp.json()
    file_id = data.get("id") or data.get("file_id")
    if not file_id:
        raise RuntimeError(f"Unexpected response: {data}")
    logger.info("Uploaded %s as file %s", file_path, file_id)
    return file_id


def submit_extraction_job(
    file_id: str,
    extraction_agent_id: str,
    overrides: Optional[Dict[str, Any]] = None,
    field_schema: Optional[Dict[str, Any]] = None,
) -> str:
    """Create an extraction job and return the job ID."""
    api_key = get_api_key()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload: Dict[str, Any] = {
        "file_id": file_id,
        "extraction_agent_id": extraction_agent_id,
    }
    if overrides:
        payload["overrides"] = overrides
    if field_schema:
        payload["field_schema"] = field_schema
    resp = _request("POST", "/api/v1/extraction/jobs", headers=headers, data=json.dumps(payload))
    data = resp.json()
    job_id = data.get("id") or data.get("job_id")
    if not job_id:
        raise RuntimeError(f"Unexpected response: {data}")
    logger.info("Started extraction job %s for file %s", job_id, file_id)
    return job_id


def poll_job(job_id: str, poll_interval: float = 2.0, timeout: float = 300.0) -> Dict[str, Any]:
    """Poll an extraction job until completion and return the result."""
    api_key = get_api_key()
    headers = {"Authorization": f"Bearer {api_key}"}
    start = time.time()
    while True:
        resp = _request("GET", f"/api/v1/extraction/jobs/{job_id}", headers=headers)
        data = resp.json()
        status = data.get("status")
        if status == "COMPLETED":
            logger.info("Job %s completed", job_id)
            return data
        if status == "FAILED":
            raise RuntimeError(f"Extraction job failed: {data}")
        if time.time() - start > timeout:
            raise TimeoutError(f"Extraction job {job_id} timed out")
        time.sleep(poll_interval)


def parse_with_llamacloud(file_path: str, extraction_agent_id: str, **kwargs) -> Dict[str, Any]:
    """Upload a file, run extraction, and return structured data."""
    file_id = upload_file(file_path)
    job_id = submit_extraction_job(file_id=file_id, extraction_agent_id=extraction_agent_id, **kwargs)
    result = poll_job(job_id)
    return result.get("result") or result.get("data") or result


__all__ = [
    "upload_file",
    "submit_extraction_job",
    "poll_job",
    "parse_with_llamacloud",
    "get_api_key",
    "set_api_key",
]
