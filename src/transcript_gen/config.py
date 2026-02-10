import dspy
from dotenv import load_dotenv

load_dotenv()

GENERATOR_LM = dspy.LM(
    "anthropic/claude-haiku-4-5-20251001",
    max_tokens=16384,
    temperature=1.0,
)

MONITOR_LM = dspy.LM(
    "anthropic/claude-opus-4-6",
    max_tokens=2048,
    temperature=0.0,
)

JUDGE_LM = dspy.LM(
    "anthropic/claude-opus-4-6",
    max_tokens=2048,
    temperature=0.0,
)

REFLECTION_LM = dspy.LM(
    "anthropic/claude-opus-4-6",
    max_tokens=4096,
    temperature=0.7,
)

dspy.configure(lm=GENERATOR_LM)
