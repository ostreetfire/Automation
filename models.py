from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    watchlist: Mapped[bool] = mapped_column(default=False)

    files: Mapped[List["File"]] = relationship(back_populates="case")

    def __repr__(self) -> str:
        return f"Case(id={self.id!r}, name={self.name!r})"


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    filename: Mapped[str] = mapped_column(String)
    hash: Mapped[Optional[str]] = mapped_column(String)
    uuid: Mapped[Optional[str]] = mapped_column(String)
    tags: Mapped[Optional[Dict]] = mapped_column(JSON)
    stored_path: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    case: Mapped[Case] = relationship(back_populates="files")

    def __repr__(self) -> str:
        return f"File(id={self.id!r}, filename={self.filename!r})"
