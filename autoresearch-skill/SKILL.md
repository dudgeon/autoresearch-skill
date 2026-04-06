---
name: autoresearch
description: Set up a Karpathy-style autoresearch loop to autonomously optimize any function, algorithm, or system in your codebase. Use when the user wants to optimize performance, improve an algorithm, tune a pipeline, maximize a metric, or mentions "autoresearch", "optimization loop", "grind on this", "let it run overnight", or "find the best strategy". Also use when they want to benchmark and iteratively improve any measurable aspect of their code.
argument-hint: "[optional: what to optimize]"
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash Write
---

# Autoresearch: Autonomous Optimization Loop Setup

This skill walks through setting up a Karpathy-style autoresearch loop on any
codebase. The pattern is simple: **one file to edit, one number to improve, one
relentless loop**. Your job is to guide the user through six phases, then hand
off to the loop.

For full pattern reference, see [references/pattern-overview.md](references/pattern-overview.md).
For eval design guidance, see [references/eval-design.md](references/eval-design.md).

## How to use this skill

Read the user's message and figure out where they are:

- **Fresh start** ("optimize my nesting algorithm") → Begin at Phase 1
- **Target known** ("I want to autoresearch `nesting.py`") → Skip to Phase 2
- **Metric known** ("maximize throughput, it's in `bench.py`") → Skip to Phase 3
- **Everything ready** ("just generate the loop prompt") → Skip to Phase 5

Be conversational. Ask one question at a time. Don't dump all six phases as a
wall of text — reveal them progressively. If the user says "just do it," make
reasonable defaults and move fast.

If `$ARGUMENTS` is provided, treat it as the initial description of what to
optimize and jump into Phase 1 with that context.

---

## Phase 1: DISCOVER — What are we optimizing?

**Goal**: Identify the function, algorithm, or system to improve, and understand
the codebase well enough to know where it lives.

1. If the user hasn't said what to optimize, ask:
   > What part of your code do you want to improve? This could be an algorithm
   > (packing, sorting, scheduling), a pipeline (data processing, build times),
   > a model (accuracy, latency), or anything with a measurable outcome.

2. Explore the codebase to understand the landscape:
   - Read the README, any docs, and the main entry points
   - Identify the module/file(s) that contain the target logic
   - Map dependencies: what does the target code import? What calls it?

3. Summarize back to the user:
   > Here's what I found: [target logic] lives in [file(s)], depends on [X],
   > and is called by [Y]. The main opportunity for optimization seems to be
   > [specific aspect]. Does that match what you had in mind?

**Output**: A clear statement of what we're optimizing and where it lives.

---

## Phase 2: DEFINE — What does "better" mean?

**Goal**: Define a single scalar metric that the loop will optimize. This is the
hardest and most important step. Read [references/eval-design.md](references/eval-design.md)
for detailed guidance.

1. Ask the user what "better" means to them. Prompt with examples relevant to
   their domain:
   > How do you measure success for this? Some examples:
   > - **Throughput**: pieces packed, requests/sec, items processed
   > - **Quality**: accuracy %, error rate, similarity score
   > - **Efficiency**: utilization %, waste %, memory usage
   > - **Speed**: latency, wall-clock time, iterations/sec
   > - **Compound**: weighted combination of the above

2. Help them collapse multiple goals into **one number**. If they have competing
   objectives (e.g., "fast AND accurate"), design a weighted composite score.
   The autoresearch pattern requires a single scalar — multiple metrics create
   ambiguity that derails autonomous optimization.

3. Determine direction: higher is better, or lower is better?

4. Identify hard constraints that must NEVER be violated (the "guardrails"):
   - Correctness invariants (no overlaps, all tests pass, valid output)
   - Resource limits (memory, time, dependencies)
   - API contracts (function signatures, return types)

5. Confirm with the user:
   > So the metric is: [description], measured by [how], where [higher/lower]
   > is better. Hard constraints: [list]. Sound right?

**Output**: Metric definition, direction, and constraint list.

---

## Phase 3: ISOLATE — Carve out the target file

**Goal**: Ensure the code to be optimized lives in a single file that the agent
can edit without touching anything else. This is the "one editable asset"
constraint from the Karpathy pattern.

1. Assess current structure:
   - Is the target logic already in one file? → Great, skip to step 4
   - Is it spread across multiple files? → Needs refactoring
   - Is it tangled with code that must not change? → Needs extraction

2. If refactoring is needed, guide it:
   - Extract the optimization target into its own module (e.g., `nesting.py`,
     `optimizer.py`, `strategy.py`)
   - Keep a clean interface: the extracted module should import from the rest of
     the codebase, but the rest should import from it through a stable API
   - The function signature that the benchmark will call must be stable

3. Verify isolation:
   - The target file should be editable without breaking imports elsewhere
   - Run existing tests to confirm the refactor didn't break anything
   - `git diff --stat` should show the refactor clearly

4. Confirm with the user:
   > The optimization target is now isolated in `[filename]`. The agent will
   > only edit this file. Everything else is off-limits. Want to review the
   > refactor before we continue?

5. Commit the refactored state:
   ```
   git add -A && git commit -m "refactor: isolate [target] for autoresearch"
   ```

**Output**: A single target file with a stable interface.

---

## Phase 4: EVALUATE — Build the benchmark harness

**Goal**: Create a Python script that runs the target code against a diverse set
of test scenarios and outputs a single composite score.

Read [references/eval-design.md](references/eval-design.md) for the full design guide.
Use [templates/benchmark-scaffold.py](templates/benchmark-scaffold.py) as a starting point.

### Design the scenario battery

1. Identify scenario categories — aim for 12-20 total scenarios:
   - **Bread-and-butter cases** (3-4): common inputs, weighted 1.5×
   - **Edge cases** (3-4): boundary conditions, unusual inputs
   - **Stress tests** (2-3): large inputs, many items, weighted 2.0×
   - **Mixed/complex cases** (2-3): combinations that exercise different code paths
   - **Should-fail cases** (1-2): inputs that should be rejected gracefully, weighted 0.5×

2. For each scenario, define:
   - Input parameters
   - Expected behavior (not exact output — the algorithm may change)
   - Weight (how much this scenario matters to the composite score)

### Design the scoring function

The composite score should be 0-100 and follow this structure:

1. **Hard gates first**: correctness violations (crashes, constraint violations)
   should tank the score to near-zero. The agent must never learn that breaking
   things is acceptable.

2. **Primary metric** (60-70% weight): the thing the user actually cares about
   (utilization, throughput, accuracy, etc.)

3. **Secondary metrics** (20-30% weight): supporting quality measures
   (waste contiguity, memory usage, code complexity)

4. **Speed bonus** (0-5% weight): minor tiebreaker for faster execution.
   Should never dominate.

### Build the harness

1. Create `benchmark_[target].py` in the project root
2. Structure:
   - `SCENARIOS` list at the top (easy to read and extend)
   - `score_scenario(scenario)` → dict of sub-scores
   - `composite_score(all_results)` → single float 0-100
   - `main()` → runs all scenarios, prints single number (or `--detail` for breakdown)
3. Test it:
   ```bash
   python benchmark_[target].py --detail
   ```
4. Verify: the score should be non-zero, non-trivial, and the `--detail` output
   should clearly show where the current algorithm is strong and weak.

5. Confirm with the user:
   > Baseline score is [X]. The weakest scenarios are [list]. The benchmark
   > runs in [N] seconds. Here's the full breakdown: [--detail output].
   > Does this capture what you care about?

**Output**: A working benchmark that prints a single score to stdout.

---

## Phase 5: PROMPT — Generate the autoresearch loop prompt

**Goal**: Create a markdown file that Claude Code can execute as an autonomous
optimization loop.

Use [templates/autoresearch-prompt.md](templates/autoresearch-prompt.md) as the
template. Fill in every field from Phases 1-4:

### Fields to populate

| Field | Source |
|-------|--------|
| GOAL | Phase 2 metric definition, in plain English |
| TARGET_FILE | Phase 3 isolated filename |
| METRIC_COMMAND | `python benchmark_[target].py` |
| METRIC_DIRECTION | Phase 2 direction |
| BASELINE | Phase 4 baseline score |
| VERIFY_COMMAND | Command that exits 0 if code is correct |
| CYCLE_TIMEOUT | Based on benchmark runtime (2-5× bench time) |
| OFF_LIMITS | Phase 2 constraints + untouchable files |
| GUARDRAILS | Phase 2 hard constraints |

### Write domain context

This is the section that makes the difference between a generic loop and one
that actually finds improvements. Include:

1. **What the code does** — enough for the agent to understand the domain
2. **Current algorithm** — how it works today, in plain English
3. **Where the waste is** — specific, concrete opportunities for improvement
4. **Ideas to explore** — seed hypotheses (non-exhaustive, to inspire the agent)
5. **Dead ends** — things you've already tried that didn't work

### Save the prompt

Save as `.claude/commands/autoresearch-[target].md` in the project so the user
can invoke it with `/autoresearch-[target]`.

Also save a copy as `autoresearch-[target].md` in the project root for reference.

**Output**: A complete, ready-to-run autoresearch prompt.

---

## Phase 6: LAUNCH — Start the loop

**Goal**: Create the branch, run the baseline, and hand off to the loop.

1. Create the working branch:
   ```bash
   git checkout -b autoresearch/[target-name]
   ```

2. Run the baseline and record it:
   ```bash
   python benchmark_[target].py --detail
   ```

3. Create `autoresearch-log.md` with Cycle 0 (baseline):
   ```markdown
   # Autoresearch Log: [target]

   ## Configuration
   - **Target file**: [filename]
   - **Metric**: [description] ([higher/lower] is better)
   - **Baseline score**: [score]
   - **Benchmark**: `python benchmark_[target].py`
   - **Started**: [timestamp]

   ## Cycle 0 — Baseline
   - **Score:** [score]
   - **Detail:** [paste --detail output]
   - **Notes:** Starting point. No changes yet.
   ```

4. Commit the setup:
   ```bash
   git add -A && git commit -m "[autoresearch] setup: benchmark + prompt for [target]"
   ```

5. Present the launch summary to the user:
   > **Ready to launch autoresearch on `[target file]`.**
   >
   > - Branch: `autoresearch/[target-name]`
   > - Baseline score: [score]
   > - Metric: [description]
   > - Benchmark: [N] scenarios in [T] seconds
   >
   > To start the loop, run:
   > ```
   > /autoresearch-[target]
   > ```
   > Or paste the contents of `autoresearch-[target].md` into a new Claude Code session.
   >
   > The agent will run indefinitely. Each improvement is committed; each failure
   > is reverted and logged. Check `autoresearch-log.md` and `git log --oneline`
   > for progress. Interrupt anytime with Ctrl+C — all work is saved.

---

## Important principles

### The three constraints (from Karpathy)

Every autoresearch setup MUST have all three. Remove any one and you need supervision:

1. **One editable file** — confines changes to a single reviewable surface
2. **One scalar metric** — makes every decision binary (better or worse)
3. **Time-boxed cycles with git checkpoints** — makes every experiment reversible

### Common mistakes to prevent

- **Multiple metrics without composition**: The agent can't optimize two numbers
  at once. Always collapse to one composite score.
- **Modifiable eval**: If the agent can edit the benchmark, it will "optimize" by
  gaming the metric. The benchmark file must be off-limits.
- **Missing correctness gates**: Without hard gates for constraint violations,
  the agent will learn to break things for marginal metric gains.
- **Overly broad target file**: If the file is too large, the agent wastes cycles
  on irrelevant code. Isolate the optimization target tightly.
- **No seed hypotheses**: The agent performs much better when the domain context
  section includes specific ideas to explore, not just "make it better."
- **Forgetting to test the benchmark**: Always run `--detail` and verify the
  scores make sense before launching the loop.

### When NOT to use autoresearch

- **Subjective quality** (writing style, UI aesthetics) — no scalar metric
- **Architecture changes** spanning many files — violates one-file constraint
- **One-shot tasks** (migrations, refactors) — no iterative improvement needed
- **Non-deterministic targets** where the metric varies per run — the agent
  can't distinguish signal from noise
