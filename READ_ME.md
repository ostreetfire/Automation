# Automation Toolkit

This repository contains a small case management and analysis framework.  It lets you store case documents, run a simple valuation pipeline and search document text using a basic RAG (Retrieval Augmented Generation) workflow.

## Directory layout

```
analysis/       - Analysis engine modules and structured financial data
agents/         - Helper agents for file storage, analysis and document search
config/         - YAML and JSON configuration files
database/       - SQLAlchemy models and helper functions
storage/        - File and vector index storage directories
utils/          - Utility functions and API clients
main.py         - Command line interface
```

## Configuration

Edit `config/settings.yaml` to provide your database URL, storage paths, API keys and Slack webhook. Example values are already present in the file. Valuation assumptions live in `config/assumptions.yaml` and watchlist case IDs are listed in `config/watchlist.json`.

## Using the CLI

The CLI in `main.py` manages cases and triggers analysis.

```
python main.py create_case --name "Example" --watchlist        # create a new case
python main.py upload_file --case 1 --path /path/to/file.pdf   # store a file
python main.py run_analysis --case 1                           # run the analysis pipeline
python main.py list_watchlist                                  # show watchlist cases
```

Uploaded files are moved under `storage/raw_files/<case_id>/YEAR/MONTH` with a JSON sidecar containing metadata.

## Analysis pipeline

`agents/analysis_agent.py` loads structured financial data from `analysis/financials/<case_id>.json`, valuation assumptions from `config/assumptions.yaml` and runs the valuation and semantic RAG steps (`analysis/engine/valuation.py` and `analysis/engine/semantic_rag.py`). Results are persisted to the `analysis_results` table.

`reporting_engine.py` can turn the JSON output into an Excel workbook or PowerPoint deck if the optional `openpyxl` or `python-pptx` packages are installed.

## Vector search

The RAG agent (`agents/rag_agent.py`) can build a vector index from stored documents and answer questions:

```
from agents.rag_agent import build_case_vector_index, query_case_docs
build_case_vector_index(["file.pdf"], case_id="1")
answer = query_case_docs("What does the contract say?", case_id="1")
```

FAISS is used by default but Chroma can be used if installed.

## Watchlist

`agents/watchlist_agent.py` monitors cases listed in `config/watchlist.json`. When a new file appears for a watchlist case it records the event and optionally posts a Slack notification using the configured webhook.

## Running tests

Tests are located in the `tests/` directory and can be run with `pytest`.

```
pytest -q
```

