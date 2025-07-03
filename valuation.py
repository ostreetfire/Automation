from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


@dataclass
class ValuationResult:
    enterprise_value: float
    methodology: str
    sensitivity: Dict[str, float]


def load_assumptions(path: str | Path) -> Dict[str, float]:
    """Load simple key:value assumptions from a YAML file."""
    assumptions: Dict[str, float] = {}
    p = Path(path)
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        assumptions[key.strip()] = float(value.strip())
    return assumptions


def _get_item(data: Any, key: str) -> Any:
    if isinstance(data, Mapping):
        return data[key]
    try:
        return data[key]
    except Exception:
        return getattr(data, key)


def dcf_valuation(financials: Any, wacc: float, growth: float) -> float:
    """Calculate enterprise value using a simple DCF model."""
    cash_flows: Sequence[float] = list(_get_item(financials, "free_cash_flow"))
    pv = 0.0
    for i, cf in enumerate(cash_flows, start=1):
        pv += cf / (1 + wacc) ** i
    terminal_cf = cash_flows[-1] * (1 + growth)
    terminal_value = terminal_cf / (wacc - growth)
    terminal_pv = terminal_value / (1 + wacc) ** len(cash_flows)
    return pv + terminal_pv


def comps_valuation(financials: Any, multiple: float, key: str = "ebitda") -> float:
    """Apply a comps multiple to a financial metric."""
    metric = float(_get_item(financials, key))
    return metric * multiple


def run_valuation(financials: Any, assumptions: Mapping[str, float]) -> ValuationResult:
    """Run DCF and comps valuations and return a JSON-ready result."""
    wacc = float(assumptions["wacc"])
    growth = float(assumptions["growth"])
    multiple = float(assumptions["comps_multiple"])

    dcf_value = dcf_valuation(financials, wacc, growth)
    comps_value = comps_valuation(financials, multiple)
    enterprise_value = (dcf_value + comps_value) / 2

    sens_high = dcf_valuation(financials, wacc * 0.9, growth)
    sens_low = dcf_valuation(financials, wacc * 1.1, growth)
    sensitivity = {"high": sens_high, "low": sens_low}

    return ValuationResult(
        enterprise_value=enterprise_value,
        methodology="DCF and Comps",
        sensitivity=sensitivity,
    )


__all__ = [
    "ValuationResult",
    "load_assumptions",
    "dcf_valuation",
    "comps_valuation",
    "run_valuation",
]
