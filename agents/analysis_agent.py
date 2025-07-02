from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None

from models import Base
from analysis.engine.valuation import perform_valuation
from analysis.engine.semantic_rag import run_semantic_rag
from database.db_connection import SessionLocal, engine
from database.analysis_results import AnalysisResult

# ensure tables exist on import
Base.metadata.create_all(engine)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_structured_financials(case_id: int) -> Dict[str, Any]:
    """Load financial data for a case from ``analysis/financials``."""
    path = Path(f"analysis/financials/{case_id}.json")
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    logger.warning("Structured financials not found for case %s", case_id)
    return {}


def load_assumptions() -> Dict[str, Any]:
    """Load valuation assumptions from ``config/assumptions.yaml``."""
    path = Path("config/assumptions.yaml")
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            if yaml:
                return yaml.safe_load(f) or {}
            # fallback: simple ``key: value`` parser if PyYAML is missing
            data = {}
            for line in f:
                if ":" in line:
                    key, value = line.strip().split(":", 1)
                    data[key.strip()] = float(value)
            return data
    logger.warning("Assumptions file not found: %s", path)
    return {}


def persist_results(case_id: int, results: Dict[str, Any]) -> None:
    """Persist analysis results for a case."""
    with SessionLocal() as session:
        record = AnalysisResult(case_id=case_id, results=results)
        session.add(record)
        session.commit()


def run_analysis_pipeline(case_id: int) -> None:
    """Execute the full analysis pipeline for a case."""
    start_time = datetime.now(timezone.utc)
    logger.info("Starting analysis for case %s at %s", case_id, start_time.isoformat())

    financials = load_structured_financials(case_id)
    assumptions = load_assumptions()
    valuation = perform_valuation(financials, assumptions)
    rag_output = run_semantic_rag(case_id)

    results = {
        "financials": financials,
        "assumptions": assumptions,
        "valuation": valuation,
        "semantic_rag": rag_output,
        "started_at": start_time.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    persist_results(case_id, results)
    logger.info("Completed analysis for case %s", case_id)


__all__ = ["run_analysis_pipeline"]
