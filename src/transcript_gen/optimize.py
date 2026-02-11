"""GEPA optimization entry point."""

import json
import logging

import dspy

from transcript_gen import config
from transcript_gen.metrics import evasion_metric
from transcript_gen.modules import TranscriptGenerator
from transcript_gen.prompt_logger import PromptLogger
from transcript_gen.tasks import get_devset, get_trainset
from transcript_gen.utils import run_output_dir

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def _save_program(program, output_dir, label="optimized"):
    """Save a program's state and print its instruction."""
    program_path = output_dir / f"{label}_program.json"
    program.save(str(program_path))
    logger.info("Saved %s program to %s", label, program_path)
    return program_path


def main():
    trainset = get_trainset(40)
    devset = get_devset(20)
    output_dir = run_output_dir()

    logger.info("Output dir: %s", output_dir)
    logger.info("Trainset: %d examples, Devset: %d examples", len(trainset), len(devset))

    prompt_logger = PromptLogger(output_dir)

    optimizer = dspy.GEPA(
        metric=evasion_metric,
        auto="light",
        reflection_lm=config.REFLECTION_LM,
        track_stats=True,
        log_dir=str(output_dir / "gepa_logs"),
        gepa_kwargs={"stop_callbacks": prompt_logger},
    )

    student = TranscriptGenerator()

    logger.info("Starting GEPA optimization...")
    try:
        optimized = optimizer.compile(
            student=student,
            trainset=trainset,
            valset=devset,
        )
    except KeyboardInterrupt:
        logger.warning("Interrupted — saving current student state...")
        _save_program(student, output_dir, label="interrupted")
        prompt_logger.write_summary()
        raise
    except Exception:
        logger.exception("GEPA optimization failed — saving current student state...")
        _save_program(student, output_dir, label="crashed")
        prompt_logger.write_summary()
        raise

    # Save optimized program
    _save_program(optimized, output_dir)
    prompt_logger.write_summary()

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
