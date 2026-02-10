"""GEPA optimization entry point."""

import json
import logging
import sys

import dspy

from transcript_gen import config
from transcript_gen.metrics import evasion_metric
from transcript_gen.modules import TranscriptGenerator
from transcript_gen.tasks import get_devset, get_trainset
from transcript_gen.utils import run_output_dir

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    trainset = get_trainset(40)
    devset = get_devset(20)
    output_dir = run_output_dir()

    logger.info("Output dir: %s", output_dir)
    logger.info("Trainset: %d examples, Devset: %d examples", len(trainset), len(devset))

    optimizer = dspy.GEPA(
        metric=evasion_metric,
        auto="light",
        reflection_lm=config.REFLECTION_LM,
        track_stats=True,
        log_dir=str(output_dir / "gepa_logs"),
    )

    student = TranscriptGenerator()

    logger.info("Starting GEPA optimization...")
    optimized = optimizer.compile(
        student=student,
        trainset=trainset,
        valset=devset,
    )

    # Save optimized program
    program_path = output_dir / "optimized_program.json"
    optimized.save(str(program_path))
    logger.info("Saved optimized program to %s", program_path)

    # Save results summary
    results = {
        "output_dir": str(output_dir),
        "trainset_size": len(trainset),
        "devset_size": len(devset),
        "optimizer": "GEPA",
        "auto": "light",
    }
    results_path = output_dir / "results.json"
    results_path.write_text(json.dumps(results, indent=2))
    logger.info("Saved results to %s", results_path)

    # Print optimized instruction
    print("\n" + "=" * 60)
    print("OPTIMIZED INSTRUCTION:")
    print("=" * 60)
    for name, predict in optimized.named_predictors():
        print(f"\n--- {name} ---")
        print(predict.signature.__doc__)

    return optimized


if __name__ == "__main__":
    main()
