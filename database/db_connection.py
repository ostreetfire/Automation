"""Database connection setup using SQLAlchemy."""

from __future__ import annotations

import yaml
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


def load_settings(path: Path = Path("config/settings.yaml")) -> dict:
    """Load YAML settings from the given path."""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


settings = load_settings()
DATABASE_URL = settings.get("database", {}).get("url", "sqlite:///local.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    """Create all tables in the database."""
    Base.metadata.create_all(engine)


__all__ = ["engine", "SessionLocal", "Base", "init_db"]
