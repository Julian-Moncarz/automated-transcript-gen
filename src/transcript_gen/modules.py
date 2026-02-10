"""DSPy modules — the optimizable components."""

import dspy

from transcript_gen.signatures import GenerateTranscript


class TranscriptGenerator(dspy.Module):
    """Wraps GenerateTranscript as an optimizable DSPy module.

    GEPA optimizes the signature's instruction (docstring) inside the
    Predict component. The monitor and judge are fixed and live in the metric.
    """

    def __init__(self):
        super().__init__()
        self.generate = dspy.Predict(GenerateTranscript)

    def forward(self, task_description: str):
        return self.generate(task_description=task_description)
