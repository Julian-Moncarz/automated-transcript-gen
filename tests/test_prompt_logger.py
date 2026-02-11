"""Unit tests for PromptLogger — no API calls."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from transcript_gen.prompt_logger import PromptLogger, _format_parents


# -- Helpers ---------------------------------------------------------------


def _make_state(
    candidates: list[dict[str, str]],
    parents: list[list[int | None]],
    scores: list[float],
    metric_calls: list[int] | None = None,
) -> MagicMock:
    """Build a minimal mock GEPAState with the fields PromptLogger reads."""
    state = MagicMock()
    state.program_candidates = candidates
    state.parent_program_for_candidate = parents
    state.program_full_scores_val_set = scores
    state.num_metric_calls_by_discovery = metric_calls or [0] * len(candidates)
    return state


# -- Tests -----------------------------------------------------------------


class TestFormatParents:
    def test_none_only(self):
        assert _format_parents([None]) == "—"

    def test_single_parent(self):
        assert _format_parents([0]) == "v000"

    def test_multiple_parents(self):
        assert _format_parents([1, 3]) == "v001, v003"

    def test_empty_list(self):
        assert _format_parents([]) == "—"


class TestPromptLoggerCall:
    """Test the stopper __call__ (live logging during optimization)."""

    def test_writes_seed_on_first_call(self, tmp_path: Path):
        logger = PromptLogger(tmp_path)
        state = _make_state(
            candidates=[{"generate": "seed prompt text"}],
            parents=[[None]],
            scores=[0.25],
        )

        result = logger(state)

        assert result is False  # never stops
        seed_file = tmp_path / "prompts" / "v000_seed.md"
        assert seed_file.exists()
        content = seed_file.read_text()
        assert "seed prompt text" in content
        assert "(seed)" in content
        assert "0.2500" in content

    def test_writes_multiple_candidates(self, tmp_path: Path):
        logger = PromptLogger(tmp_path)

        # First call: seed only
        state1 = _make_state(
            candidates=[{"generate": "seed"}],
            parents=[[None]],
            scores=[0.20],
        )
        logger(state1)

        # Second call: two new candidates appeared
        state2 = _make_state(
            candidates=[
                {"generate": "seed"},
                {"generate": "evolved v1"},
                {"generate": "evolved v2"},
            ],
            parents=[[None], [0], [0, 1]],
            scores=[0.20, 0.35, 0.50],
            metric_calls=[0, 10, 20],
        )
        logger(state2)

        assert (tmp_path / "prompts" / "v000_seed.md").exists()
        assert (tmp_path / "prompts" / "v001.md").exists()
        assert (tmp_path / "prompts" / "v002.md").exists()

        v1 = (tmp_path / "prompts" / "v001.md").read_text()
        assert "evolved v1" in v1
        assert "v000" in v1  # parent reference
        assert "0.3500" in v1

        v2 = (tmp_path / "prompts" / "v002.md").read_text()
        assert "evolved v2" in v2
        assert "v000, v001" in v2  # multiple parents

    def test_no_duplicate_writes(self, tmp_path: Path):
        """Calling with same state twice should not re-write files."""
        logger = PromptLogger(tmp_path)
        state = _make_state(
            candidates=[{"generate": "seed"}],
            parents=[[None]],
            scores=[0.20],
        )

        logger(state)
        seed_file = tmp_path / "prompts" / "v000_seed.md"
        mtime1 = seed_file.stat().st_mtime_ns

        # Calling again with same number of candidates
        logger(state)
        mtime2 = seed_file.stat().st_mtime_ns

        assert mtime1 == mtime2

    def test_missing_component_name(self, tmp_path: Path):
        """Handles candidates that don't have the expected component key."""
        logger = PromptLogger(tmp_path, component_name="generate")
        state = _make_state(
            candidates=[{"other_component": "some text"}],
            parents=[[None]],
            scores=[0.10],
        )

        logger(state)
        content = (tmp_path / "prompts" / "v000_seed.md").read_text()
        assert "<component not found>" in content


class TestWriteSummary:
    def test_summary_after_three_candidates(self, tmp_path: Path):
        logger = PromptLogger(tmp_path)
        state = _make_state(
            candidates=[
                {"generate": "seed"},
                {"generate": "v1"},
                {"generate": "v2"},
            ],
            parents=[[None], [0], [1]],
            scores=[0.20, 0.35, 0.50],
            metric_calls=[0, 10, 25],
        )
        logger(state)
        path = logger.write_summary()

        assert path == tmp_path / "prompts" / "SUMMARY.md"
        content = path.read_text()

        # Header
        assert "Prompt Evolution Summary" in content
        assert "Candidates: 3" in content

        # Table rows
        assert "v000" in content
        assert "v001" in content
        assert "v002" in content

        # Best marker on v002 (highest score)
        lines = content.splitlines()
        v002_line = [line for line in lines if "v002" in line][0]
        assert "*" in v002_line

        # v000 should not have best marker
        v000_line = [line for line in lines if "v000" in line][0]
        assert "*" not in v000_line

    def test_summary_with_no_candidates(self, tmp_path: Path):
        """Edge case: summary called before any stopper callback."""
        logger = PromptLogger(tmp_path)
        path = logger.write_summary()

        content = path.read_text()
        assert "Candidates: 0" in content

    def test_summary_links_to_version_files(self, tmp_path: Path):
        logger = PromptLogger(tmp_path)
        state = _make_state(
            candidates=[{"generate": "seed"}, {"generate": "v1"}],
            parents=[[None], [0]],
            scores=[0.20, 0.40],
        )
        logger(state)
        content = logger.write_summary().read_text()

        assert "[v000](v000_seed.md)" in content
        assert "[v001](v001.md)" in content


class TestVersionFileContent:
    """Verify the structure and content of individual version markdown files."""

    def test_seed_file_structure(self, tmp_path: Path):
        logger = PromptLogger(tmp_path)
        state = _make_state(
            candidates=[{"generate": "My seed strategy prompt"}],
            parents=[[None]],
            scores=[0.3210],
            metric_calls=[0],
        )
        logger(state)

        content = (tmp_path / "prompts" / "v000_seed.md").read_text()

        # Title
        assert content.startswith("# Strategy Prompt v000  (seed)")
        # Metadata table
        assert "| Parent | — |" in content
        assert "| Val Score | 0.3210 |" in content
        assert "| Metric Calls | 0 |" in content
        # Separator
        assert "---" in content
        # Prompt body
        assert "My seed strategy prompt" in content

    def test_evolved_file_structure(self, tmp_path: Path):
        logger = PromptLogger(tmp_path)
        state = _make_state(
            candidates=[
                {"generate": "seed"},
                {"generate": "Evolved strategy with new tactics"},
            ],
            parents=[[None], [0]],
            scores=[0.20, 0.55],
            metric_calls=[0, 15],
        )
        logger(state)

        content = (tmp_path / "prompts" / "v001.md").read_text()

        assert content.startswith("# Strategy Prompt v001")
        assert "(seed)" not in content
        assert "| Parent | v000 |" in content
        assert "| Val Score | 0.5500 |" in content
        assert "| Metric Calls | 15 |" in content
        assert "Evolved strategy with new tactics" in content
