from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

import requests
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from agents.file_organizer_agent import compute_sha256


WATCHLIST_PATH = Path("config/watchlist.json")
STATE_PATH = Path("watchlist_state.json")
LOG_PATH = Path("watchlist.log")
DB_PATH = "sqlite:///watchlist.db"

Base = declarative_base()
engine = create_engine(DB_PATH)
SessionLocal = sessionmaker(bind=engine)


class WatchlistEvent(Base):
    __tablename__ = "watchlist_events"

    id = Column(Integer, primary_key=True)
    case_id = Column(String)
    message = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(engine)


def _load_watchlist() -> List[Dict[str, str]]:
    if WATCHLIST_PATH.exists():
        with WATCHLIST_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _load_state() -> Dict[str, Dict[str, str]]:
    if STATE_PATH.exists():
        with STATE_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_state(state: Dict[str, Dict[str, str]]) -> None:
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _log_event(message: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {message}\n")


def _record_event(session: Session, case_id: str, message: str) -> None:
    event = WatchlistEvent(case_id=case_id, message=message)
    session.add(event)
    session.commit()


def send_slack_alert(webhook_url: str, message: str) -> None:
    try:
        requests.post(webhook_url, json={"text": message}, timeout=5)
    except requests.RequestException as exc:
        logging.error("Failed to send Slack alert: %s", exc)


def _check_case(case_id: str, state: Dict[str, Dict[str, str]], session: Session) -> List[str]:
    case_dir = Path("storage/raw_files") / case_id
    if not case_dir.exists():
        return []

    messages = []
    files = sorted(case_dir.glob("**/*"))
    files = [f for f in files if f.is_file()]
    last_hash = state.get(case_id, {}).get("hash")

    if not files:
        return []

    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    file_hash = compute_sha256(latest_file)

    if file_hash != last_hash:
        state[case_id] = {"hash": file_hash, "filename": latest_file.name}
        msg = f"New file for case {case_id}: {latest_file.name}"
        _record_event(session, case_id, msg)
        _log_event(msg)
        messages.append(msg)

    return messages


def run_watchlist_check(slack_webhook: Optional[str] = None) -> None:
    watchlist = _load_watchlist()
    state = _load_state()

    session = SessionLocal()
    all_messages: List[str] = []

    for item in watchlist:
        case_id = str(item.get("case_id"))
        messages = _check_case(case_id, state, session)
        all_messages.extend(messages)

    _save_state(state)

    for message in all_messages:
        if slack_webhook:
            send_slack_alert(slack_webhook, message)


__all__ = ["run_watchlist_check", "send_slack_alert"]
