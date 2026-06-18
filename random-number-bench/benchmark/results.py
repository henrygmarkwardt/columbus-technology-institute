import json
from pathlib import Path


def load_results(path: Path) -> list:
    """Load the results JSON array from disk."""
    return json.loads(Path(path).read_text())


def save_result(path: Path, record: dict) -> None:
    """Append a result record to the results JSON file."""
    path = Path(path)
    results = load_results(path)
    results.append(record)
    path.write_text(json.dumps(results, indent=2))
