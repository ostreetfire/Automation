#!/bin/bash
set -e

# Create directories for Lean MVP
mkdir -p analysis/engine analysis/templates agents database storage/raw_files storage/processed_files utils config

# Mapping of old paths to new paths
moves=(
  "10-K Extractor/COMPANY.py|analysis/engine/company_profile.py"
  "10-K Extractor/RISKS.py|analysis/engine/key_risks.py"
  "10-K Extractor/LIQUIDITY.py|analysis/engine/liquidity.py"
  "10-K Extractor/DEBT.py|analysis/engine/debt_details.py"
  "10-K Extractor/CAST.py|analysis/engine/capital_structure.py"
  "10-K Extractor/RELATED_PARTY.py|analysis/engine/related_party.py"
  "10-K Extractor/AUDIT_MATTERS.py|analysis/engine/audit_matters.py"
  "10-K Extractor/report.py|agents/tenk_report_agent.py"
  "DIP Agent/generate_terms_slide.py|analysis/engine/dip_terms.py"
  "DIP Agent/generate_drawdown_slide.py|analysis/engine/dip_drawdown.py"
  "DIP Agent/generate_budget_slide.py|analysis/engine/dip_budget.py"
  "DIP Agent/generate_dip_slides.py|agents/dip_slides_agent.py"
  "FDD Extractor/CASE_OVERVIEW.py|analysis/engine/case_overview.py"
  "FDD Extractor/FINANCIALS.PY|analysis/engine/financials.py"
  "FDD Extractor/PREPETITION.py|analysis/engine/prepetition.py"
  "FDD Extractor/SPECIAL_COMMITTEE.py|analysis/engine/special_committee.py"
  "FDD Extractor/generate_bankruptcy_report.py|agents/bankruptcy_report_agent.py"
)

for pair in "${moves[@]}"; do
  IFS='|' read -r src dst <<< "$pair"
  if [ -f "$src" ]; then
    mkdir -p "$(dirname "$dst")"
    # Only move if destination doesn't already exist
    if [ ! -f "$dst" ]; then
      mv "$src" "$dst"
    fi
  fi
done

# Remove stale compiled files
rm -f __pycache__/app.cpython-312.pyc

# Placeholder files required by MVP
placeholders=(
  "main.py"
  "analysis/engine/valuation.py"
  "analysis/engine/semantic_rag.py"
  "analysis/engine/reporting.py"
  "agents/analysis_agent.py"
  "agents/watchlist_agent.py"
  "agents/file_organizer_agent.py"
  "database/db_connection.py"
  "database/cases.py"
  "database/files.py"
  "database/analysis_results.py"
  "database/watchlist_items.py"
  "utils/helpers.py"
  "config/settings.yaml"
)

for file in "${placeholders[@]}"; do
  if [ ! -f "$file" ]; then
    mkdir -p "$(dirname "$file")"
    touch "$file"
  fi
done

exit 0
