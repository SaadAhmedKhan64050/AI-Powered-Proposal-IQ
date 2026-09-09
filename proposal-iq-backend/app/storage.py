"""
Minimal file-based persistence for pipeline runs, keyed by run_id.

Deliberately not a database — for a 5-day sprint with a non-developer user,
"a JSON file per run" is easier to explain, inspect, and debug than standing
up Postgres. Swap for a real DB later if this needs to scale past a demo.
"""
import json
from pathlib import Path

RUNS_DIR = Path("outputs") / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)


def save_run(run_id: str, data: dict) -> None:
    path = RUNS_DIR / f"{run_id}.json"
    path.write_text(json.dumps(data, indent=2, default=str))


def load_run(run_id: str) -> dict | None:
    path = RUNS_DIR / f"{run_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())
