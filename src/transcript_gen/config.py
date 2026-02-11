import dspy
from dotenv import load_dotenv

load_dotenv()

# CLIProxyAPI routes requests through Claude Max subscription
PROXY_BASE = "http://localhost:8317/v1"
PROXY_KEY = "68f40441f00f4faa067b9a8c0ac99d97"

GENERATOR_LM = dspy.LM(
    "openai/claude-haiku-4-5-20251001",
    max_tokens=16384,
    temperature=1.0,
    api_base=PROXY_BASE,
    api_key=PROXY_KEY,
)

MONITOR_LM = dspy.LM(
    "openai/claude-opus-4-6",
    max_tokens=2048,
    temperature=0.0,
    api_base=PROXY_BASE,
    api_key=PROXY_KEY,
)

JUDGE_LM = dspy.LM(
    "openai/claude-haiku-4-5-20251001",
    max_tokens=2048,
    temperature=0.0,
    api_base=PROXY_BASE,
    api_key=PROXY_KEY,
)

REFLECTION_LM = dspy.LM(
    "openai/claude-haiku-4-5-20251001",
    max_tokens=4096,
    temperature=0.7,
    api_base=PROXY_BASE,
    api_key=PROXY_KEY,
)

dspy.configure(lm=GENERATOR_LM)
