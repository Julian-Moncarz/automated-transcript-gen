"""Log each GEPA candidate's strategy prompt to markdown during optimization."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from gepa.core.state import GEPAState

logger = logging.getLogger(__name__)


class PromptLogger:
    """StopperProtocol-compatible callback that writes each candidate prompt to markdown.

    Implements ``__call__(gepa_state) -> bool`` so it can be passed as a
    ``stop_callback`` to GEPA.  Always returns False (never stops the run).
    """

    def __init__(self, output_dir: Path, component_name: str = "generate"):
        self.prompts_dir = output_dir / "prompts"
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.component_name = component_name
        self._num_logged: int = 0
        # Accumulated data for the summary (avoids re-reading files).
        self._scores: list[float | None] = []
        self._parents: list[list[int | None]] = []
        self._metric_calls: list[int] = []

    # -- StopperProtocol -------------------------------------------------

    def __call__(self, gepa_state: GEPAState) -> bool:
        candidates = gepa_state.program_candidates
        scores = gepa_state.program_full_scores_val_set
        parents = gepa_state.parent_program_for_candidate
        metric_calls = gepa_state.num_metric_calls_by_discovery

        for idx in range(self._num_logged, len(candidates)):
            score = scores[idx] if idx < len(scores) else None
            parent = parents[idx] if idx < len(parents) else []
            calls = metric_calls[idx] if idx < len(metric_calls) else None
            self._write_version(idx, candidates[idx], score, parent, calls)
            self._scores.append(score)
            self._parents.append(parent)
            self._metric_calls.append(calls)

        self._num_logged = len(candidates)
        return False  # never stop

    # -- Public helpers ---------------------------------------------------

    def write_summary(self) -> Path:
        """Write ``prompts/SUMMARY.md`` from accumulated data.  Call after optimization."""
        best_idx = None
        best_score = -1.0
        for i, s in enumerate(self._scores):
            if s is not None and s > best_score:
                best_score = s
                best_idx = i

        lines = [
            "# Prompt Evolution Summary\n",
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n",
            f"Candidates: {self._num_logged}\n",
            "",
            "| Version | Parent | Val Score | Metric Calls | Best |",
            "|---------|--------|-----------|--------------|------|",
        ]
        for i in range(self._num_logged):
            parent_str = _format_parents(self._parents[i]) if i < len(self._parents) else "—"
            score_str = f"{self._scores[i]:.4f}" if self._scores[i] is not None else "—"
            calls_str = str(self._metric_calls[i]) if self._metric_calls[i] is not None else "—"
            star = " * " if i == best_idx else ""
            lines.append(f"| [v{i:03d}](v{i:03d}{'_seed' if i == 0 else ''}.md) "
                         f"| {parent_str} | {score_str} | {calls_str} | {star} |")

        path = self.prompts_dir / "SUMMARY.md"
        path.write_text("\n".join(lines) + "\n")
        logger.info("Wrote prompt summary to %s", path)
        return path

    # -- Internals --------------------------------------------------------

    def _write_version(
        self,
        idx: int,
        candidate: dict[str, str],
        score: float | None,
        parents: list[int | None],
        metric_calls: int | None,
    ) -> Path:
        filename = f"v{idx:03d}{'_seed' if idx == 0 else ''}.md"
        prompt_text = candidate.get(self.component_name, "<component not found>")
        parent_str = _format_parents(parents)
        score_str = f"{score:.4f}" if score is not None else "pending"
        calls_str = str(metric_calls) if metric_calls is not None else "—"

        content = (
            f"# Strategy Prompt v{idx:03d}{'  (seed)' if idx == 0 else ''}\n"
            f"\n"
            f"| Field | Value |\n"
            f"|-------|-------|\n"
            f"| Parent | {parent_str} |\n"
            f"| Val Score | {score_str} |\n"
            f"| Metric Calls | {calls_str} |\n"
            f"\n"
            f"---\n"
            f"\n"
            f"{prompt_text}\n"
        )

        path = self.prompts_dir / filename
        path.write_text(content)
        logger.info("Wrote prompt v%03d to %s (score=%s)", idx, path, score_str)
        return path


def _format_parents(parents: list[int | None]) -> str:
    parts = [f"v{p:03d}" for p in parents if p is not None]
    return ", ".join(parts) if parts else "—"
