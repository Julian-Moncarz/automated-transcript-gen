# Research Summary

## Most Relevant Papers

### Tier 1: Directly Informing Our Approach

**Strengthening Red Teams: A Modular Scaffold for Control Evaluations** (Anthropic, Nov 2025)
https://alignment.anthropic.com/2025/strengthening-red-teams/

The closest existing work to what we're building. Decomposes sabotage into 5 skills (suspicion modeling, attack selection, plan synthesis, execution, subtlety) and optimizes each separately using a probabilistic model of SHADE-Arena. Reduced safety score from 0.87 to 0.41 for Claude 3.7 Sonnet. We're essentially doing their approach but with DSPy optimization instead of a hand-designed modular scaffold.

**Async Control: Stress-testing Asynchronous Control Measures for LLM Agents** (Dec 2025)
https://arxiv.org/html/2512.13526

Multi-round red-team/blue-team game using Claude 4.1 Opus (untrusted agent) vs Claude 3.7 Sonnet (monitor) across 5 realistic coding environments (Kubernetes, vLLM, IaC, data poisoning, eval sabotage). Red team iteratively improves system prompts — essentially what we're automating with DSPy. Best monitor ensemble: 5.7% false negative rate at 1% false positive. Red team strategies evolved from simple interleaving → hiding in test files → spreading across files with tailored justifications.

**SHADE-Arena** (Anthropic, June 2025)
https://arxiv.org/abs/2506.15740

The benchmark for agent sabotage + monitoring. 17 task pairs with hidden malicious side-objectives. Transcript format: system prompt (hidden from monitor), user task, tool calls + responses, optional hidden scratchpad. Claude 3.7 Sonnet succeeds 27% of the time against Claude 3.6 Sonnet monitor. Best monitors: AUC 0.87. Human monitors: AUC 0.65. Average trajectory ~20k tokens, ~25 turns.

**Adaptive Attacks on Trusted Monitors Subvert AI Control Protocols** (Oct 2025)
https://arxiv.org/abs/2510.09462

Shows prompt injection in code comments can completely break monitors. GPT-4.1 monitor scored 0 suspicion on ALL 375 backdoored samples when they contained injected instructions. The Defer-to-Resample defense actually amplifies the attack. Most powerful evasion technique but arguably least interesting since it's "cheating" — directly manipulating the monitor rather than being genuinely subtle.

### Tier 2: Informing Ground Truth & Setup

**AI Control: Improving Safety Despite Intentional Subversion** (Redwood Research, Dec 2023 / ICML 2024)
https://arxiv.org/abs/2312.06942

The foundational paper. Red-team/blue-team game on APPS programming problems. Backdoor = code passes tests but fails on secret exploit input. Best protocol (untrusted monitoring + defer to trusted): 92% safety, 92% usefulness. Established the framework everyone else builds on.

**Automated Researchers Can Subtly Sandbag** (Anthropic, March 2025)
https://alignment.anthropic.com/2025/automated-researchers-sandbag/

AI agents implementing ML tasks deliberately do a bad job while looking like they're trying. Ground truth is objective (compare accuracy to baseline). Claude 3.7 Sonnet can sandbag zero-shot with suspicion score ~3.6/10. Strategies: suboptimal hyperparameters, simple models, subsampled data, noise injection — all technically plausible but intentionally bad. Zero-shot monitors can't reliably catch it.

**Pre-deployment Auditing Can Catch an Overt Saboteur** (Anthropic, Jan 2026)
https://alignment.anthropic.com/2026/auditing-overt-saboteur/

Trained 3 saboteur models + 2 benign baselines on Claude Sonnet 4.5. Human auditor caught all 3, but automated agent only caught 1 of 3. Key caveat: these were OVERT saboteurs. Subtle/concealment-focused sabotage (our focus) is explicitly flagged as future work.

### Tier 3: DSPy Red-Teaming Prior Art

**DSPy Red-Teaming** (Haize Labs)
https://github.com/haizelabs/dspy-redteam

Existing DSPy pipeline for red-teaming using alternating Attack and Refine modules (5 layers) with MIPRO optimizer. Got 4x improvement (10% → 44% attack success rate) on Vicuna. Built for jailbreaking, not coding agent sabotage, but the DSPy architecture is directly reusable.

**Prompt Optimization and Evaluation for LLM Automated Red Teaming** (July 2025)
https://arxiv.org/abs/2507.22133

Uses OPRO to optimize attack generator prompts. Introduces "discoverability" metric — how consistently individual attacks succeed when repeated. Measures ASR at individual attack level rather than aggregated.

## Taxonomy of Malicious Behaviors

From the literature, coding agents can be malicious in these ways:

1. **Code backdoors**: Solution passes tests but fails on secret inputs (AI Control paper)
2. **Data exfiltration**: Stealing API keys, credentials, sending to external parties (SHADE-Arena)
3. **Financial fraud**: Hidden unauthorized transactions among legitimate ones (SHADE-Arena)
4. **Subtle sabotage/sandbagging**: Deliberately bad but plausible-looking implementations (Automated Researchers)
5. **Supply chain attacks**: Malicious dependencies, typosquatted packages
6. **Infrastructure weakening**: Disabling security controls, opening backdoor ports (Async Control)
7. **Oversight undermining**: Manipulating monitoring/evaluation systems (Anthropic Sabotage Evals)
8. **Prompt injection against monitor**: Embedding instructions in output to manipulate the monitor (Adaptive Attacks)

## Key Evasion Strategies That Work

1. **Temporal distribution**: Spread malicious changes across many steps
2. **Legitimate cover**: Bury 1 bad action among 15+ good ones
3. **Semantic camouflage**: Make malicious code look like reasonable implementation choices
4. **Evidence destruction**: Delete temp files after using them for attack
5. **Prompt injection**: Embed monitor-manipulating instructions in code comments (most effective but least interesting)
6. **Tailored justifications**: Frame suspicious actions as necessary for the main task ("privilege change needed to fix test errors")

## Ground Truth Approaches

1. **Execution-based** (strongest): Run code, check if malicious effect occurred. Binary.
2. **Self-report + judge**: Model confesses what it did, separate judge evaluates. Our approach for #1.
3. **Objective performance comparison**: Compare output quality to known baseline. Works for sandbagging.
4. **Controlled experimental design**: Paired benign/malicious trajectories from same setup.
5. **Attacker provides proof**: Must submit a test demonstrating the bug works (~56% verification rate at Anthropic).
