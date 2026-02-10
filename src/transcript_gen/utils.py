import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_score(raw: str) -> int:
    """Extract an integer score from LLM output.

    Handles formats like "85", "Score: 85", "<score>85</score>", "85/100".
    """
    # Try <score>N</score> format first
    m = re.search(r"<score>\s*(\d+)\s*</score>", raw)
    if m:
        return _clamp(int(m.group(1)))

    # Try bare integer or "N/100"
    m = re.search(r"\b(\d{1,3})\b", raw)
    if m:
        return _clamp(int(m.group(1)))

    logger.warning("Could not parse score from: %s", raw[:200])
    return 0


def _clamp(value: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, value))


def run_output_dir(base: str = "outputs") -> Path:
    """Create and return a timestamped run directory."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    d = Path(base) / f"run_{ts}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def append_jsonl(path: Path, obj: dict) -> None:
    """Append a JSON object as a line to a JSONL file."""
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n")
