from __future__ import annotations

import json
import logging
from datetime import datetime
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_structured_financials(case_id: int) -> Dict[str, Any]:
    path = Path(f"analysis/financials/{case_id}.json")
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    logger.warning("Structured financials not found for case %s", case_id)
    return {}


def load_assumptions() -> Dict[str, Any]:
    path = Path("config/assumptions.yaml")
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            if yaml:
                return yaml.safe_load(f) or {}
            # fallback very simple parser: key: value pairs separated by ':'
            data = {}
            for line in f:
                if ":" in line:
                    key, value = line.strip().split(":", 1)
                    data[key.strip()] = float(value)
            return data
    logger.warning("Assumptions file not found: %s", path)
    return {}


def persist_results(case_id: int, results: Dict[str, Any]) -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        record = AnalysisResult(case_id=case_id, results=results)
        session.add(record)
        session.commit()


def run_analysis_pipeline(case_id: int) -> None:
    start_time = datetime.utcnow()
    logger.info("Starting analysis for case %s", case_id)

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
        "completed_at": datetime.utcnow().isoformat(),
    }

    persist_results(case_id, results)
    logger.info("Completed analysis for case %s", case_id)


__all__ = ["run_analysis_pipeline"]
