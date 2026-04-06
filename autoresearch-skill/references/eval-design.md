# Evaluation Harness Design Guide

The benchmark harness is the single most important artifact in an autoresearch
setup. A bad eval teaches the agent bad habits. A good eval guides the agent
toward genuinely useful improvements.

## The cardinal rule

**The agent will optimize exactly what you measure, and nothing else.**

If your metric rewards speed but doesn't penalize correctness, the agent will
find ways to be fast by being wrong. If your metric doesn't distinguish between
"good" and "perfect," the agent will plateau at "good." Design your metric as
if you're writing a loss function for training a model — because that's
essentially what it is.

## Harness anatomy

```python
#!/usr/bin/env python3
"""Benchmark harness for autoresearch. Outputs single score 0-100."""

import sys, time

SCENARIOS = [ ... ]        # 12-20 test cases

def score_scenario(s):     # → dict of sub-scores
    ...

def composite_score(all):  # → float 0-100
    ...

def main():
    detail = "--detail" in sys.argv
    results = []
    for s in SCENARIOS:
        r = score_scenario(s)
        results.append((s["name"], r, s.get("weight", 1.0)))
        if detail:
            print(f"  {s['name']}: {format_result(r)}")
    score = composite_score(results)
    if detail:
        print(f"\nCOMPOSITE SCORE: {score}")
    else:
        print(score)
```

The harness MUST support two modes:
- **Plain mode** (`python benchmark.py`): prints a single number to stdout.
  This is what the loop's METRIC_COMMAND calls.
- **Detail mode** (`python benchmark.py --detail`): prints per-scenario
  breakdown plus the composite. This is what the human reads.

## Scenario design

### Categories (aim for 12-20 total)

| Category | Count | Weight | Purpose |
|----------|-------|--------|---------|
| Bread-and-butter | 3-4 | 1.5× | Common real-world inputs |
| Edge cases | 3-4 | 1.0× | Boundary conditions, unusual inputs |
| Stress tests | 2-3 | 2.0× | Large inputs, many items, adversarial |
| Mixed/complex | 2-3 | 1.5× | Combinations exercising different paths |
| Should-fail | 1-2 | 0.5× | Inputs that must be rejected gracefully |

### Scenario specification

Each scenario should be a dict with at minimum:
```python
{
    "name": "descriptive_snake_case_name",
    "weight": 1.0,        # relative importance
    # ... domain-specific input parameters
    "expect_fail": False,  # True for should-fail scenarios
}
```

### Writing good scenarios

- **Name them descriptively**: `tight_fit_24x12` not `test_3`. The name appears
  in logs and must be self-explanatory.
- **Cover the input space**: vary all dimensions — size, count, shape, density,
  configuration. Don't just test "small, medium, large."
- **Include adversarial cases**: inputs designed to exploit weaknesses in the
  current algorithm. These drive the most improvement.
- **Weight by importance**: scenarios the user encounters most often should count
  more. Exotic edge cases should count less.
- **Keep them fast**: each scenario should complete in under 5 seconds. The full
  battery should finish in under 30 seconds.

## Scoring function design

### The hierarchy of concerns

```
1. CORRECTNESS (hard gate)
   ↓ if correct
2. PRIMARY METRIC (60-70% weight)
   ↓
3. SECONDARY METRICS (20-30% weight)
   ↓
4. SPEED BONUS (0-5% weight)
```

### Correctness as a hard gate

Correctness violations must catastrophically tank the score — but not to
absolute zero. The agent needs a gradient to follow even when things are broken.

```python
if overlaps > 0 or out_of_bounds > 0:
    # Tank the score, but leave a gradient
    violation_penalty = 0.1 * (overlaps + out_of_bounds)
    scenario_score = max(0.0, 0.3 - violation_penalty)
```

Why not zero? If a change causes 1 overlap and the score is 0.0, the agent
learns nothing about which direction to go. At 0.25, it knows "this is bad but
close" vs. 0.05 "this is very bad."

### Primary metric

This is the thing the user actually cares about. Design it to be:
- **Normalized** (0.0 to 1.0): so it's composable with other sub-scores
- **Monotonic**: strictly better inputs always produce strictly better scores
- **Sensitive**: small real improvements should produce detectable score changes.
  If the score is stuck at 0.73 for 20 cycles, the granularity is too coarse.

### Secondary metrics

These capture quality aspects the user cares about but that shouldn't dominate.
Examples: waste contiguity, code complexity, memory efficiency, latency variance.

### Speed bonus

Keep this tiny (2-5%). Speed matters, but it should never override correctness
or quality. It's a tiebreaker between otherwise-equal solutions.

### Composite formula

```python
def composite_score(all_results):
    total_score = 0.0
    total_weight = 0.0
    for name, result, weight in all_results:
        scenario_score = compute_scenario_score(result)  # 0.0-1.0
        total_score += scenario_score * weight
        total_weight += weight
    return round((total_score / total_weight) * 100, 4)
```

Normalize to 0-100 for human readability. Four decimal places give the agent
enough precision to detect small improvements.

## Should-fail scenarios

These test graceful error handling for impossible inputs. Scoring:
- Graceful rejection (sys.exit with message): full marks
- Unexpected success (algorithm got smarter): also full marks
- Unhandled crash (traceback): partial marks (0.2)

```python
if expect_fail:
    if error and not ran:
        score = 1.0  # graceful rejection
    elif ran:
        score = 1.0  # unexpectedly succeeded
    else:
        score = 0.2  # crashed
```

## Correctness checks

Build these as standalone functions that return counts of violations:

```python
def check_overlaps(placements, min_gap):
    """Returns number of overlapping pairs."""
    ...

def check_bounds(placements, bounds):
    """Returns number of out-of-bounds items."""
    ...
```

For large item counts, sample pairwise checks rather than checking all O(n²)
pairs. Use a fixed random seed for reproducibility.

## Testing your benchmark

Before launching the loop, verify:

1. **Baseline score is non-trivial**: not 0, not 100, ideally 50-80
2. **Detail output is readable**: each scenario's result makes sense
3. **Correctness gates work**: temporarily introduce a bug and verify the
   score drops catastrophically
4. **Metric is sensitive**: make a known-good change (even a trivial one)
   and verify the score moves in the right direction
5. **Runtime is acceptable**: the full suite should finish in <30 seconds
6. **Scores are reproducible**: run twice, get the same number

## Common mistakes

- **Testing with only one scenario**: the agent overfits to that single case
- **Equal weights for all scenarios**: exotic edge cases dominate over common
  use cases
- **No correctness gates**: the agent learns to break things
- **Metric too coarse**: score rounds to the same value for meaningfully
  different algorithms
- **Metric depends on random seeds**: non-determinism makes it impossible to
  distinguish signal from noise
- **Benchmark takes too long**: if each cycle is 5 minutes, the agent runs
  12 experiments per hour instead of 60
- **Importing from the target file**: if the benchmark imports helper functions
  from the file being optimized, changes to the target can break the benchmark.
  Import only stable interfaces.
