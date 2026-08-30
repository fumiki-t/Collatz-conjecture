# Phase 24 run results — sparse arcs and area-two cycles

Status: accepted exact derivations and bounded computations; the Collatz
conjecture remains `OPEN`; `proves_collatz=false`.

## Result

The sparse circular-arc lift converts a sparse slope-root congruence into an
integer `R_arc` with `D|R_arc`, a strict size bound, and parity-based
nonvanishing when every nonzero coefficient is odd.  Applying it to the exact
area-two profile classification proves that every hypothetical positive
nontrivial coprime cycle profile has defect area at least three.

The critical large-`q` step uses EXT05.  The noncritical large-length step is
internal.  All remaining cases are independently enumerated.

## Exact finite scope

- 7,057 critical coprime area-two profiles through `q<=60`;
- 204 noncritical coprime area-two profiles with `L<=21`;
- 544,073 critical area-two profiles in a direct modular scan through
  `q<=250`;
- zero integral profiles in all three declared area-two scopes;
- 521,154 critical coprime area-three profiles through `q<=100`;
- worst one-sided q-arc ratio `35/41`;
- worst two-sided diagnostic ratio `80/94`;
- zero exact EXT05-threshold failures in that finite area-three scope.

The area-three scan is `VERIFIED_FINITE`, not a theorem for all `q`.

## Reproduction

```bash
.venv/bin/python src/phase24_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase24.py \
  --artifact-dir artifacts --write-report artifacts/phase24_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase24_properties.py tests/test_phase24_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

The independent verifier reconstructs weak profiles and literal exponent
words, uses a shifted Bezout pair, checks the opposite largest-gap tie, and
imports no production code.  Final timings, test counts, commit provenance,
and the manifest digest are recorded in the accepted experiment manifest.

## Evidence

- [`research/audits/sparse-arc-resultants/REPORT.md`](research/audits/sparse-arc-resultants/REPORT.md)
- `artifacts/phase24_theory.json`
- `artifacts/phase24_area_two_remainder.json`
- `artifacts/phase24_area_three_diagnostic.json`
- `artifacts/phase24_regressions.json`
- `artifacts/phase24_obstruction_report.md`
- `artifacts/phase24_verifier.json`
- `artifacts/SHA256SUMS`

## What this result does not prove

It does not exclude area-three or arbitrary-area coprime cycles, noncoprime
cycles, any nonperiodic counterexample branch, or the Collatz conjecture.
The generic seven-point bound is insufficient, and H147 remains `OPEN`.
`proves_collatz=false`.
