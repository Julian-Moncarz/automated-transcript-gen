"""Evaluate an optimized (or baseline) program on the devset."""

import json
import logging
import sys
from pathlib import Path

import dspy

from transcript_gen import config
from transcript_gen.metrics import evasion_metric
from transcript_gen.modules import TranscriptGenerator
from transcript_gen.tasks import get_devset
from transcript_gen.utils import append_jsonl, run_output_dir

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    # Load program — either from a saved file or use baseline
    program_path = sys.argv[1] if len(sys.argv) > 1 else None

    if program_path:
        logger.info("Loading optimized program from %s", program_path)
        program = TranscriptGenerator()
        program.load(program_path)
    else:
        logger.info("No program path provided, using baseline (seed strategy)")
        program = TranscriptGenerator()

    devset = get_devset(20)
    output_dir = run_output_dir()
    samples_path = output_dir / "samples.jsonl"

    # Resume from existing samples if restarting a crashed run
    completed_tasks: set[str] = set()
    if samples_path.exists():
        with open(samples_path) as f:
            for line in f:
                row = json.loads(line)
                completed_tasks.add(row["task_description"])
        logger.info("Resuming: %d samples already completed", len(completed_tasks))

    logger.info("Evaluating on %d dev examples...", len(devset))

    scores = []
    for i, example in enumerate(devset):
        if example.task_description in completed_tasks:
            logger.info("Sample %d/%d: SKIPPED (already completed)", i + 1, len(devset))
            continue

        logger.info("Sample %d/%d: %s", i + 1, len(devset), example.task_description[:60])

        try:
            pred = program(task_description=example.task_description)
            result = evasion_metric(example, pred)
        except Exception:
            logger.exception("Sample %d/%d failed, skipping", i + 1, len(devset))
            continue

        scores.append(result.score)

        append_jsonl(samples_path, {
            "task_description": example.task_description,
            "transcript": pred.transcript,
            "confession": pred.confession,
            "score": result.score,
            "feedback": result.feedback,
        })

        logger.info("  Score: %.3f", result.score)

    # Summary
    avg = sum(scores) / len(scores) if scores else 0.0
    results = {
        "program_path": program_path,
        "num_samples": len(scores),
        "mean_score": avg,
        "min_score": min(scores) if scores else 0.0,
        "max_score": max(scores) if scores else 0.0,
        "scores": scores,
    }

    results_path = output_dir / "results.json"
    results_path.write_text(json.dumps(results, indent=2))

    print(f"\n{'='*60}")
    print(f"EVALUATION RESULTS ({len(scores)} samples)")
    print(f"{'='*60}")
    print(f"Mean score: {avg:.3f}")
    print(f"Min:  {min(scores) if scores else 0:.3f}")
    print(f"Max:  {max(scores) if scores else 0:.3f}")
    print(f"\nResults saved to {results_path}")
    print(f"Samples saved to {samples_path}")


if __name__ == "__main__":
    main()
