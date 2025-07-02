import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))

from pathlib import Path
import json
import builtins
import types

import pytest

from valuation import load_assumptions, dcf_valuation, comps_valuation, run_valuation, ValuationResult


def test_load_assumptions(tmp_path: Path) -> None:
    yaml_content = """
    wacc: 0.1
    growth: 0.03
    comps_multiple: 6
    """
    f = tmp_path / "assumptions.yml"
    f.write_text(yaml_content)
    data = load_assumptions(f)
    assert data["wacc"] == 0.1
    assert data["growth"] == 0.03
    assert data["comps_multiple"] == 6


def test_dcf_comps_and_run_valuation() -> None:
    financials = {
        "free_cash_flow": [100.0, 110.0, 120.0],
        "ebitda": 150.0,
    }
    assumptions = {"wacc": 0.1, "growth": 0.03, "comps_multiple": 6}

    dcf_val = dcf_valuation(financials, 0.1, 0.03)
    assert dcf_val > 0

    comps_val = comps_valuation(financials, 6)
    assert comps_val == 900.0

    result = run_valuation(financials, assumptions)
    assert isinstance(result, ValuationResult)
    assert result.enterprise_value > 0
    assert "high" in result.sensitivity and "low" in result.sensitivity
