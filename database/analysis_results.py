from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from models import Base, Case


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    results: Mapped[Dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    case: Mapped[Case] = relationship()

    def __repr__(self) -> str:
        return f"AnalysisResult(id={self.id!r}, case_id={self.case_id!r})"


__all__ = ["AnalysisResult"]
