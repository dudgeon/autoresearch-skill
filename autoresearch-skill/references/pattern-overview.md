# Autoresearch Pattern Reference

## Origin

Andrej Karpathy released the autoresearch pattern on March 7, 2026, via
[github.com/karpathy/autoresearch](https://github.com/karpathy/autoresearch).
It emerged from his work on nanochat (a minimal LLM training codebase), where
he had AI agents autonomously iterating on the training code while he slept.
Over a 2-day run the agent executed ~700 experiments, found 20 genuine
improvements (2.9% hit rate), and collectively achieved an 11% speedup on
already-optimized code.

Karpathy explicitly described it not as a tool to install, but as a "recipe/idea"
to give to your agent and apply to whatever you care about.

## The three-file architecture

Only three files matter:

| File | Who edits | Purpose |
|------|-----------|---------|
| `prepare.py` (or equivalent eval harness) | Nobody — immutable | Data prep, evaluation, metric computation. Guarantees every experiment is measured against the same yardstick. |
| `train.py` (or target file) | Agent only | The single file the agent may modify. Contains all optimization-eligible code. |
| `program.md` (or loop prompt) | Human only | Plain-language markdown instructions: what to optimize, constraints, research direction. The agent's entire "orchestration framework." |

## The three constraints

Every autoresearch setup requires all three. Remove any one and you need supervision:

1. **One editable asset** — confines the agent to a single file. Every hypothesis
   is a git diff. Prevents the agent from "cheating" by modifying evaluation code.

2. **One scalar metric** — eliminates ambiguous tradeoffs. Multiple metrics create
   confusion that derails autonomous optimization. A single number makes every
   decision binary: better or worse.

3. **One time-boxed cycle with git checkpoints** — makes every experiment
   reversible. Each cycle: hypothesize → implement → measure → commit or revert.
   The ratchet only moves forward.

## The loop

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  1. ORIENT    Read target file + experiment log     │
│       ↓                                             │
│  2. HYPOTHESIZE   State one specific hypothesis     │
│       ↓                                             │
│  3. IMPLEMENT     Smallest change that tests it     │
│       ↓                                             │
│  4. VERIFY        Run correctness checks            │
│       ↓           (fail? → revert, log, goto 1)     │
│  5. MEASURE       Run metric command, compare       │
│       ↓                                             │
│  6. DECIDE        Better? → commit. Worse? → revert │
│       ↓                                             │
│  7. LOG           Record hypothesis + result        │
│       ↓                                             │
│  8. CONTINUE      Go to 1. NEVER STOP.              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## The `program.md` is the real innovation

The markdown file carries three registers simultaneously:
- **Instructions**: what to search for
- **Constraints**: what must not change
- **Research direction**: seed hypotheses and domain context

No other format handles all three. YAML encodes structure but not reasoning.
Python is executable but not legible as strategy. JSON has no narrative.
Markdown sits at the intersection of human editability and agent parseability.

The agent's context window IS the state machine. There are no state graphs, no
tool schemas, no routing logic, no supervisor agents.

## What the human does

The human's role is NOT to run experiments. It is to:

1. **Define "better"** — choose the metric, design the eval
2. **Encode domain knowledge** — write the program.md with enough context that
   the agent doesn't waste cycles on obviously bad ideas
3. **Review the git log** — validate that accepted changes are real improvements,
   not metric-gaming artifacts
4. **Iterate on the prompt** — if the agent is stuck in a local minimum,
   rewrite program.md to redirect exploration

## Key results from the original run

- ~700 experiments in 2 days on a single GPU
- 20 genuine improvements (2.9% hit rate)
- All 20 stacked additively and transferred to larger models
- 11% faster "Time to GPT-2" (2.02h → 1.80h)
- Specific finds: missing QK-Norm scalar, incorrect AdamW betas, too-conservative
  banded attention, missing Value Embedding regularization

Karpathy's assessment: "It's not novel, ground-breaking 'research' (yet), but
all the adjustments are 'real', I didn't find them manually previously, and they
stack up."

## Generalizability

The pattern works for any domain with:
- A single file to optimize
- A single measurable metric
- Fast feedback (experiments complete in minutes, not hours)
- Deterministic evaluation (same code → same score)

| Domain | Editable asset | Scalar metric | Fixed constraint |
|--------|---------------|---------------|------------------|
| ML training | train.py | val_bpb | Dataset, tokenizer |
| Nesting/packing | nesting.py | composite pack score | Shape geometry, spacing |
| Database queries | query_config | p95 latency | Schema, benchmark data |
| RAG pipeline | retrieval.py | faithfulness score | Document corpus, eval Qs |
| Prompt engineering | system.md | binary eval pass rate | Eval harness |
| Frontend perf | component.tsx | Lighthouse score | Test suite |
| Compiler opts | optimizer.py | benchmark runtime | Correctness tests |
