from __future__ import annotations

import argparse
from pathlib import Path
from pprint import pprint

from sqlalchemy.orm import Session

from models import Case, File
from agents.file_organizer_agent import store_file
from agents.analysis_agent import analyze
from database import SessionLocal


def create_case(args: argparse.Namespace) -> None:
    """Create a new case."""
    name = args.name or input("Case name: ").strip()
    watchlist = args.watchlist

    with SessionLocal() as session:
        if session.query(Case).filter_by(name=name).first():
            print(f"Case '{name}' already exists")
            return
        case = Case(name=name, watchlist=watchlist)
        session.add(case)
        session.commit()
        pprint({"id": case.id, "name": case.name, "watchlist": case.watchlist})


def upload_file(args: argparse.Namespace) -> None:
    """Upload a file to a case."""
    case_id = args.case or input("Case ID: ").strip()
    path_str = args.path or input("Path to file: ").strip()
    upload_path = Path(path_str)

    if not upload_path.is_file():
        print(f"File '{upload_path}' does not exist")
        return

    with SessionLocal() as session:
        case = session.get(Case, int(case_id))
        if not case:
            print(f"No case with id {case_id}")
            return
        result = store_file(upload_path, str(case.id))
        meta = result["metadata"]
        file_record = File(
            case_id=case.id,
            filename=meta["original_filename"],
            hash=meta["hash"],
            uuid=meta["uuid"],
            stored_path=meta["stored_path"],
        )
        session.add(file_record)
        session.commit()
        pprint(meta)


def run_analysis(args: argparse.Namespace) -> None:
    """Run analysis on a case."""
    case_id = args.case or input("Case ID: ").strip()

    with SessionLocal() as session:
        case = session.get(Case, int(case_id))
        if not case:
            print(f"No case with id {case_id}")
            return
        analyze(case.id)


def list_watchlist(_: argparse.Namespace) -> None:
    """List watchlist cases."""
    with SessionLocal() as session:
        cases = session.query(Case).filter_by(watchlist=True).all()
        pprint([{"id": c.id, "name": c.name} for c in cases])


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Case management CLI")
    sub = parser.add_subparsers(dest="command")

    create = sub.add_parser("create_case", help="Create a new case")
    create.add_argument("--name", help="Case name")
    create.add_argument("--watchlist", action="store_true", help="Flag case as watchlist item")
    create.set_defaults(func=create_case)

    upload = sub.add_parser("upload_file", help="Upload file to case")
    upload.add_argument("--case", type=int, help="Case ID")
    upload.add_argument("--path", help="Path to file")
    upload.set_defaults(func=upload_file)

    analysis = sub.add_parser("run_analysis", help="Run analysis on case")
    analysis.add_argument("--case", type=int, help="Case ID")
    analysis.set_defaults(func=run_analysis)

    watch = sub.add_parser("list_watchlist", help="List watchlist cases")
    watch.set_defaults(func=list_watchlist)

    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    try:
        args.func(args)
    except Exception as exc:  # pragma: no cover - simple CLI error handling
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
