# Worked Example: Couch Spacer Nesting Optimization

This example walks through how the autoresearch skill was used to set up an
optimization loop for a CNC nesting algorithm. Use it as a reference for how
each phase maps to real artifacts.

## The problem

A Python tool generates trapezoidal "couch spacer" shapes and nests them onto
rectangular stock sheets for CNC cutting. The nesting algorithm packs customer
orders first, then fills remaining space with standard inventory pieces. The
goal: pack as many total spacers as possible while minimizing waste.

## Phase 1: DISCOVER

**Codebase scan revealed:**
- `spacer_nester.py` — monolithic file containing shape generation, nesting
  algorithm, DXF output, preview, and CLI
- The nesting logic (~150 lines) was tangled with shape geometry (~80 lines)
  and output formatting (~100 lines)
- The nesting algorithm tried 4 strategies (0°/180° and 90°/270° row packing,
  each with normal and rotated stock) and picked the one fitting the most pieces

**Optimization target identified:** the nesting algorithm itself — specifically
`row_nest()`, `_try_layout()`, `_pack_row()`, and the pair offset calculation.

## Phase 2: DEFINE

**Discussion with user:**
> "I want to pack the most total spacers, including all orders and as many
> standard inventory pieces as possible. Unused stock should be as contiguous
> as possible — one large scrap piece is better than many slivers."

**Metric design:**
- Primary (65%): stock utilization (piece area / stock area)
- Secondary (25%): waste contiguity (Herfindahl-Hirschman Index on waste regions)
- Tertiary (8%): inventory fill ratio
- Tiebreaker (2%): speed bonus
- Direction: **higher is better**

**Hard constraints (gates):**
- No piece overlaps (minimum spacing: 1mm)
- No pieces outside stock boundary
- ALL order pieces must be placed before any inventory
- Valid DXF output (shapes are CNC-cut on real material)

## Phase 3: ISOLATE

**Refactored:** Extracted all nesting logic from `spacer_nester.py` into a
standalone `nesting.py` module:
- `nesting.py` imports shape/geometry functions from `spacer_nester.py`
- `spacer_nester.py` imports `row_nest()` from `nesting.py`
- Clean interface: `row_nest(orders, stock_w, stock_h, spacing) → (placements, inv_count, strategy_name)`

**Committed:** `git commit -m "refactor: isolate nesting algorithm for autoresearch"`

## Phase 4: EVALUATE

**17 scenarios designed:**

| Category | Scenarios | Examples |
|----------|-----------|----------|
| Bread-and-butter (×1.5) | 3 | 6 pairs on 24×12, 10 pairs on 48×24 |
| Mixed sizes (×1.5-2.0) | 2 | 2 sizes on 24×24, 3 sizes on 48×24 |
| Tight fits (×2.0) | 2 | 12 pieces on 24×12, wide pieces |
| Inventory-only (×1.0) | 2 | Fill 24×12, fill 48×48 |
| Odd stock (×1.0) | 3 | 12×36 narrow, 12×8 small, 96×48 large |
| Stress (×2.0) | 1 | 5 different sizes on 48×48 |
| Spacing variation (×0.8) | 2 | 0.5mm tight, 2.0mm wide |
| Should-fail (×0.5) | 2 | Oversized pieces, overfilled stock |

**Correctness checks built:**
- `check_overlaps()`: pairwise distance check on placed pieces (sampled for >40 pieces)
- `check_bounds()`: bounding box check against stock dimensions
- Both use Shapely for accurate polygon geometry with arc approximation

**Baseline result:** 74.92 / 100

**Weakness analysis from --detail:**
- Utilization ranged from 58% (mixed sizes) to 80% (large fill-only)
- Stress test with 5 sizes scored lowest (58.6% utilization)
- Row-based packing wastes vertical space between rows (taper shape)

## Phase 5: PROMPT

**Key prompt sections written:**

### Domain context included:
- Shape description (trapezoidal, 18-vertex, 4° taper, lip + notch)
- Current algorithm explanation (4 strategies, pair packing, binary search offsets)
- Where the waste is (between rows, row ends, size transitions, limited strategies)

### Seed hypotheses provided:
- Row interleaving (vertical overlap between tapered rows)
- Bottom-notch nesting (concave notch accepts neighboring lip)
- Multi-angle strategies (45°/225° pairs, mixed per-row)
- Smarter row composition (compatible sizes sharing rows)
- End-of-row optimization (different rotations for singles)
- Partial-row inventory (fill gaps in last order row)
- Grid search on pair offsets (y-staggering within pairs)
- Recursive fill (fit pieces into large waste polygons)

### Off-limits specified:
- `benchmark_nesting.py` (eval harness)
- Shape generation functions in `spacer_nester.py`
- DXF output, preview, CLI interface
- Placement dataclass fields
- `row_nest()` function signature

## Phase 6: LAUNCH

```bash
git checkout -b autoresearch/nesting-density
python benchmark_nesting.py --detail   # baseline: 74.92
# Created autoresearch-log.md with Cycle 0
git add -A && git commit -m "[autoresearch] setup: benchmark + prompt for nesting"
```

**Prompt saved to:**
- `.claude/commands/autoresearch-nesting.md` (invokable as `/autoresearch-nesting`)
- `autoresearch-nesting.md` (reference copy in project root)

**Launched with:** `/autoresearch-nesting`

## Files produced

```
project/
├── nesting.py                              ← TARGET FILE (agent edits this)
├── benchmark_nesting.py                    ← EVAL HARNESS (immutable)
├── autoresearch-nesting.md                 ← LOOP PROMPT (reference copy)
├── autoresearch-log.md                     ← EXPERIMENT LOG (agent appends)
├── .claude/commands/autoresearch-nesting.md ← LOOP PROMPT (invokable)
├── spacer_nester.py                        ← shape geometry (off-limits)
└── ...
```

## Lessons from this setup

1. **The refactor was essential.** The original monolithic file meant the agent
   would have been free to modify shape geometry, DXF output, and CLI code —
   none of which should change. Isolation made the off-limits boundary crisp.

2. **17 scenarios was the right count.** Fewer would have left blind spots;
   more would have slowed the benchmark beyond the 30-second target.

3. **Waste contiguity was worth measuring.** Without it, the agent could have
   achieved high utilization by scattering tiny pieces into every gap, producing
   unusable scrap. The HHI metric rewards clean, contiguous waste regions.

4. **Seed hypotheses accelerated early cycles.** The agent's first 5 cycles
   targeted ideas from the prompt rather than exploring blindly.

5. **The should-fail scenarios caught a regression.** An early change caused
   the algorithm to crash (instead of exit gracefully) on impossible inputs.
   The should-fail scoring detected this immediately.
