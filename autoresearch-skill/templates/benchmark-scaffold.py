#!/usr/bin/env python3
"""Benchmark harness for autoresearch: {{TARGET_NAME}}

Runs a battery of scenarios and produces a single composite score (0-100).
Higher score = better.

Usage:
    python {{BENCHMARK_FILE}}          # single score to stdout
    python {{BENCHMARK_FILE}} --detail # per-scenario breakdown + score

IMPORTANT: This file is OFF-LIMITS to the autoresearch agent.
Do not modify it during an autoresearch loop.
"""

import sys
import time

# --- Import the target module ---
# Only import the stable interface. Do NOT import internal helpers
# from the target file — changes to those would break the benchmark.
#
# from {{TARGET_MODULE}} import {{TARGET_FUNCTION}}


# ---------------------------------------------------------------------------
# Test scenarios
# ---------------------------------------------------------------------------
# Design guidelines:
#   - 12-20 scenarios total
#   - Name them descriptively (they appear in logs)
#   - Include bread-and-butter, edge, stress, mixed, and should-fail cases
#   - Weight common cases higher (1.5×), stress tests higher (2.0×),
#     should-fail cases lower (0.5×)

SCENARIOS = [
    # --- Bread and butter (common real-world inputs) ---
    {
        "name": "standard_case_1",
        "weight": 1.5,
        # ... domain-specific parameters ...
    },
    {
        "name": "standard_case_2",
        "weight": 1.5,
        # ...
    },

    # --- Edge cases ---
    {
        "name": "edge_minimum_input",
        "weight": 1.0,
        # ...
    },
    {
        "name": "edge_boundary_condition",
        "weight": 1.0,
        # ...
    },

    # --- Stress tests ---
    {
        "name": "stress_large_input",
        "weight": 2.0,
        # ...
    },
    {
        "name": "stress_many_items",
        "weight": 2.0,
        # ...
    },

    # --- Mixed / complex ---
    {
        "name": "mixed_complex_1",
        "weight": 1.5,
        # ...
    },

    # --- Should-fail (graceful error handling) ---
    {
        "name": "impossible_input",
        "weight": 0.5,
        "expect_fail": True,
        # ...
    },
]


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def score_scenario(scenario):
    """Run one scenario and return a dict of sub-scores.

    Returns:
        dict with at minimum:
            ran: bool - did the target code execute without crashing?
            error: str | None - error message if it crashed
            expect_fail: bool - is this a should-fail scenario?
            primary_metric: float - the main thing we're optimizing (0-1)
            correctness_violations: int - count of constraint violations
            # ... any domain-specific sub-scores ...
    """
    expect_fail = scenario.get("expect_fail", False)

    result = {
        "ran": False,
        "error": None,
        "expect_fail": expect_fail,
        "primary_metric": 0.0,
        "correctness_violations": 0,
        "time_s": 0.0,
    }

    t0 = time.time()
    try:
        # --- Call the target function ---
        # output = target_function(**scenario_params)
        result["ran"] = True
        pass  # Replace with actual call

    except SystemExit as e:
        result["error"] = str(e)
        result["time_s"] = time.time() - t0
        return result
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
        result["time_s"] = time.time() - t0
        return result

    result["time_s"] = time.time() - t0

    # --- Compute sub-scores ---
    # result["primary_metric"] = compute_primary(output)     # 0.0-1.0
    # result["secondary_metric"] = compute_secondary(output) # 0.0-1.0
    # result["correctness_violations"] = check_correctness(output)

    return result


def composite_score(all_results):
    """Compute a single scalar 0-100 from all scenario results.

    Scoring hierarchy:
        1. Correctness violations → tank the score (hard gate)
        2. Primary metric → 65% weight
        3. Secondary metrics → 25% weight
        4. Speed bonus → ~2% weight (tiebreaker)
    """
    total_score = 0.0
    total_weight = 0.0

    for name, result, weight in all_results:
        expect_fail = result["expect_fail"]

        if expect_fail:
            # Should-fail scenarios: reward graceful handling
            if result["error"] and not result["ran"]:
                scenario_score = 1.0  # Graceful rejection
            elif result["ran"]:
                scenario_score = 1.0  # Unexpectedly succeeded — also fine
            else:
                scenario_score = 0.2  # Unhandled crash

        elif not result["ran"]:
            scenario_score = 0.0  # Failed to run

        elif result["correctness_violations"] > 0:
            # Correctness violation: tank score but leave a gradient
            penalty = 0.1 * result["correctness_violations"]
            scenario_score = max(0.0, 0.3 - penalty)

        else:
            # Success path
            primary = result["primary_metric"]          # 0-1
            secondary = result.get("secondary_metric", 0.5)  # 0-1
            speed_bonus = max(0.0, 0.02 - result["time_s"] * 0.001)

            scenario_score = (
                0.65 * primary +
                0.25 * secondary +
                0.08 * result.get("fill_ratio", 0.5) +
                speed_bonus
            )

        total_score += scenario_score * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0
    return round((total_score / total_weight) * 100, 4)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    detail = "--detail" in sys.argv
    all_results = []

    for scenario in SCENARIOS:
        name = scenario["name"]
        weight = scenario.get("weight", 1.0)

        if detail:
            print(f"  Running: {name} ...", end=" ", flush=True)

        result = score_scenario(scenario)

        if detail:
            if result["ran"]:
                print(
                    f"✓ primary={result['primary_metric']:.3f}, "
                    f"{result['time_s']*1000:.0f}ms"
                    + (f" ⚠ {result['correctness_violations']} violations"
                       if result['correctness_violations'] else "")
                )
            elif result["expect_fail"]:
                err_preview = (result['error'] or 'unknown')[:60]
                print(f"✓ (expected fail: {err_preview})")
            else:
                err_preview = (result['error'] or 'unknown')[:80]
                print(f"✗ ERROR: {err_preview}")

        all_results.append((name, result, weight))

    score = composite_score(all_results)

    if detail:
        print(f"\n{'='*50}")
        print(f"COMPOSITE SCORE: {score}")
        print(f"{'='*50}")
    else:
        print(score)


if __name__ == "__main__":
    main()
