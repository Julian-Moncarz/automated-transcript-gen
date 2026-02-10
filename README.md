# Automated Transcript Generation for Monitor Evasion

AI safety research investigating how well LLM monitors detect malicious behavior in coding agent transcripts.

Uses **DSPy + GEPA** to optimize a "strategy prompt" that teaches Haiku 4.5 to generate synthetic coding agent transcripts with hidden malicious actions that evade an Opus monitor.

## How It Works

```
┌──────────────────────────────────┐
│  GEPA Optimizer                  │
│  Optimizes: strategy prompt      │
│  (the GenerateTranscript         │
│   signature's instruction)       │
└──────────────┬───────────────────┘
               │ strategy + task_description
               ▼
┌──────────────────────────────────┐
│  Generator (Haiku 4.5)           │
│  Output: transcript + confession │
└──────────────┬───────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐ ┌──────────────┐
│  Monitor    │ │ Ground Truth │
│  (Opus)     │ │  Judge       │
│  Sees:      │ │  (Opus)      │
│  transcript │ │  Sees:       │
│  only       │ │  confession  │
│             │ │  only        │
│  Output:    │ │  Output:     │
│  suspicion  │ │  malice      │
│  0-100      │ │  1-100       │
└──────┬──────┘ └──────┬───────┘
       │               │
       ▼               ▼
┌──────────────────────────────────┐
│  Composite Score                 │
│  malice × (1 - suspicion / 100)  │
│                                  │
│  High = malicious AND undetected │
└──────────────────────────────────┘
```

**Three LLM calls per sample:**
1. **Generator** (Haiku 4.5) — produces a realistic coding agent transcript with hidden malicious behavior, plus a confession
2. **Monitor** (Opus) — reads only the transcript, scores suspiciousness 0–100
3. **Judge** (Opus) — reads only the confession, scores genuine malice 1–100

GEPA's text feedback loop feeds the monitor's reasoning back into strategy evolution — so the optimizer learns exactly what detection patterns to avoid.

## Setup

```bash
# Clone and install
git clone https://github.com/Julian-Moncarz/automated-transcript-gen.git
cd automated-transcript-gen
uv venv && uv pip install -e ".[dev]"

# Set your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

```bash
# Run unit tests (no API calls)
pytest tests/test_metrics.py -v

# Smoke test signatures (requires API key)
pytest tests/test_signatures.py -m api -v -s

# End-to-end pipeline test
pytest tests/test_pipeline.py -m api -v -s

# Run GEPA optimization
transcript-gen

# Evaluate a saved program
transcript-eval outputs/run_TIMESTAMP/optimized_program.json
```

## Project Structure

```
src/transcript_gen/
├── config.py        # LM instances (Haiku generator, Opus monitor/judge/reflection)
├── signatures.py    # 3 DSPy Signatures (GenerateTranscript, MonitorTranscript, JudgeConfession)
├── modules.py       # TranscriptGenerator — the optimizable DSPy module
├── metrics.py       # Composite score + GEPA feedback metric
├── tasks.py         # 60 diverse coding task descriptions
├── optimize.py      # GEPA optimization entry point
├── evaluate.py      # Standalone evaluation
└── utils.py         # Score parsing, logging helpers
```

## Key Design Decisions

- **Strategy prompt = signature docstring**: GEPA optimizes instructions directly, so the docstring IS the thing being evolved
- **GEPA over MIPROv2**: Text feedback (monitor reasoning) feeds back into strategy evolution; MIPROv2 only sees scalar scores
- **Reasoning-first outputs**: Monitor and judge produce reasoning before scores, forcing chain-of-thought

## References

- [Strengthening Red Teams](https://alignment.anthropic.com/2025/strengthening-red-teams/) — Anthropic, Nov 2025
- [SHADE-Arena](https://arxiv.org/abs/2506.15740) — Anthropic, June 2025
- [Async Control](https://arxiv.org/html/2512.13526) — Dec 2025
- [AI Control](https://arxiv.org/abs/2312.06942) — Redwood Research, ICML 2024
