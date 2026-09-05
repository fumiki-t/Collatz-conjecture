# Phase 40 — normalized height, Bellman geodesics, predecessor clouds

Base: `93b2c7f937d0a28fc43aee33f23786249dfa0e8d` (Phase 39 acceptance).
Branch: `feat/phase40-normalized-height-bellman`.
Proposal: `phase40_normalized_height_bellman.md`, SHA-256
`207a43feea04136e3e18444f669886ac0c843d09e2b8bf5675e14d194536510c`.
The attachment is an unaudited input, not mathematical authority. The
[`complete proof audit`](research/audits/normalized-height-bellman/REPORT.md)
records accepted arguments, quantifiers, repairs and boundaries.

## Results and repaired scope

- P242: normalized height is finite for every positive odd nonperiodic
  source, not only safe ones. Its coalescent scaling and finite sublevel sets
  give a minimum within each nonempty permanent-safe shared-future class.
- P243: a minimizer maximizes every prefix coefficient against all positive
  literal competitors. Unsafe competitors are rescued at their strict
  coefficient valley. Canonical positivity and odd/full-prefix bridges
  give `H112 => no positive nonperiodic orbit`, **without X02**.
- P244: Bellman redundancy is bounded, nondecreasing and eventually stable.
  A positive redundancy permits a height replacement **at most half** as
  large. This yields finitely many replacements, not an effective stopping
  certificate or a known bound on the last redundancy increase.
- P245: exponent-shortened predecessors form a positive integral,
  equal-time collision-free cloud under the nonperiodicity hypothesis.
- P246: for every real p>rho_star the all-step moment
  `sum_j(2^e_j/(x_j+1))^p` converges. This is already a direct P221 corollary
  of `2^e/(x+1)<3/x_next`, not an independent new exclusion principle.
- NG43: safety need not survive a tail-weight gain with adjusted initial
  run. The exact smallest tail length in the complete declared domain is 25.

P243's `VERIFIED_THEOREM` label applies to the proved logical implication,
not the still-open premise H112 or actual nonperiodic exclusion. P240 stays
historically `CONDITIONAL`; H112, H72 and H133 stay `OPEN`. No new external
theorem or literature-wide novelty claim is introduced.

## Exact finite evidence

| Audit | Complete declared scope and result |
|---|---|
| Bellman | 1,024 rows, odd starts 1..255, eight odd steps; 448 finite normalization splits; maximum observed redundancy 7 |
| Safety minimality | All 33,554,431 zero-prefixed tails through ell=25; all initial runs reduced to exact threshold intervals, with no arbitrary R cutoff |
| First failure | No failing pair through ell=24; exactly four at ell=25, each failing at one R |
| Length-25 layer | 16,777,216 paths, 7,160,480 vertices, 13,488,484 positive-weight-gain pairs |
| Clouds | 65,536 exact transitions and 12,954 alternate predecessors, odd starts 1..4095, 32 odd steps |
| Regression boundary | Six mandatory families, NG22/NG24/NG41/NG42, source167, positive periodic cloud control, negative cycles and both length-25 witnesses |

The first failure under (tail length, original tail lexicographic,
alternative tail lexicographic, initial run) is:

```text
v  = 0110110110110010110101101
v' = 0011111111111011100001100
J=173991363, weights15/16, minimum runs4/4, target run4, alternative run3.
328539247 --safe target--> 711248276
164269623 --unsafe shorter competitor--> 711248276
```

The supplied J=166692291 example is also length-minimal, but not
lexicographically first. Its quoted safe suffix is exactly 23 bits and its
actual source is 151044095, not its canonical source49151; these differ by
18*2^23. Full safety still requires checking or strict-valley rescue.

These finite ordinary orbits are not asserted to be nonperiodic. For example,
the source21 cloud {5,1} collides at equal times after entering the known
cycle. The safe gain-one control63/31 at endpoint91 demonstrates the exact
half-factor algebra, not a nonperiodic example.

## Independent reconstruction and reproducibility

The generator uses forward affine/DAG propagation and inverse Dijkstra
search. The verifier uses positional affine and zero-position sums,
parity-cylinder lifting, and exact-total-length inverse feasibility. It
imports no search implementation and reconstructs every accepted count,
row digest, witness and boundary flag. Complete mask enumeration is different
from inheriting forward DAG states; threshold entries are additionally
checked with Python arbitrary-precision integers. C++ packed arithmetic has
explicit overflow bounds, with no floating-point acceptance decisions.

Requirements: the repository Python environment and a C++17 compiler named
`c++` (no new Python package). The complete C++ enumerators use temporary
binaries and bounded working memory; no large disposable tail corpus is
committed. The experiment manifest was created before the runs.

```bash
.venv/bin/python src/phase40_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase40.py \
  --artifact-dir artifacts --output artifacts/phase40_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase40_properties.py tests/test_phase40_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q \
  tests/test_phase15b_properties.py tests/test_phase16_properties.py \
  tests/test_phase19_properties.py tests/test_phase37_properties.py \
  tests/test_phase38_properties.py tests/test_phase38_verifier.py \
  tests/test_phase39_properties.py tests/test_phase39_verifier.py
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

Actual acceptance results and code commit are recorded in
[`the experiment manifest`](research/experiments/phase40-normalized-height-bellman.json).

Phase 40 properties, verifier/tamper tests and research-health tests:
**83 passed in 55.54s**. Directly used dependency tests: **89 passed in
147.63s**. The four generator outputs were regenerated in a separate temporary
directory and matched byte-for-byte. The independent verifier returned
`valid=true`, `generator_imported=false`, and `proves_collatz=false`.
The initial control-plane pass found a stale AI guide; it was updated and
the complete focused set rerun. The index link and trailing whitespace were
also repaired. Markdown links validate across 149 files.
The CI-equivalent set was also run from a clean detached worktree of
implementation commit `966efed344885ca22735326d6cd46863d89c4de2`:
**89 passed in 335.21s**, including six additional Phase 24 verifier tests.
This gives **178 distinct scoped tests**, not a fresh whole-repository run.
The worktree was clean before and after testing. Strict research health
returned `valid=true`, no errors or warnings, 324 claims and 270 tracked
artifacts; all 270 manifest entries matched. Reproduce the CI-equivalent set
with the focused command above plus `tests/test_phase24_verifier.py`.

## Evidence and SHA-256

SHA-256 of `artifacts/SHA256SUMS`:
`81b43e3ebd23eb8309bb19fbff2ed4edc891a1e87c91781d7445451366236a43`.

- [`Bellman and normalization`](artifacts/phase40_bellman.json)
- [`complete bounded safety minimality`](artifacts/phase40_safety_minimality.json)
- [`predecessor clouds and moments`](artifacts/phase40_cloud.json)
- [`retained regressions`](artifacts/phase40_regressions.json)
- [`independent verifier result`](artifacts/phase40_verifier.json)
- [`SHA-256 manifest`](artifacts/SHA256SUMS)

## What this result does not prove

It does not prove H112, exclude any positive infinite safe source without
an additional theorem, recognize the last Bellman jump, force an improving
ancestor at every stage, or exclude arbitrary-area positive cycles.
Normalized-height decrease need not decrease ordinary source order.
Tail-length minimality is relative to the explicitly enumerated word domain.
The moment is compatible with the surviving infinite branch.
The Collatz conjecture remains `OPEN`; `proves_collatz=false`.
