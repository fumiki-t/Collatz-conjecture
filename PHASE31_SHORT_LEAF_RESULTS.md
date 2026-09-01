# Phase 31 v2 results — short-leaf double-hit repair

The cycle-side T31-A--D proposal was independently audited on
`feat/phase31-short-leaf-double-hit`.  The all-fixed-`R` pruning family repairs
the old Phase 31 residual-density gap.  The H89 numerical proposal was kept
out of scope. `proves_collatz=false`.

## Accepted claims

- `P191 VERIFIED_THEOREM`: short-leaf pruning and
  `E_R<=h+floor(Sigma/R)`.
- `P192 VERIFIED_THEOREM`: the finite radius-`R` context, type-capacity, and
  double-hit inequality.
- `P193 VERIFIED_THEOREM`: the all-fixed-`R` limit yields `xy>=2ell`, validates
  the P187 area constant, and forces normalized slack `z=0` at equality.
- `P194 VERIFIED_THEOREM`: equality forces global exact-two singleton
  incidence outside only `o(L)` starts and an `o(L)` anchor-shift mismatch.
- `E44 VERIFIED_FINITE`: complete independent `q<=9`, `R=1,2,3`, all-width
  reconstruction.

`H172`, `H133`, and `H89` remain `OPEN`.  NG40 remains the counterexample to
the obsolete single-radius inference; the new theorem survives it by using
the whole fixed-`R` family.

## Reproduction

```text
.venv/bin/python src/phase31_short_leaf_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase31_short_leaf.py --artifact-dir artifacts --output artifacts/phase31_short_leaf_verifier.json
.venv/bin/python -m pytest -q tests/test_phase31_short_leaf_properties.py tests/test_phase31_short_leaf_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/research_health.py --strict
cd artifacts && shasum -a 256 -c SHA256SUMS
```

Acceptance evidence:

- focused suite: `13 passed in 110.76s`;
- full suite: `447 passed in 1575.37s`;
- strict research health: `valid=true`, no errors or warnings;
- evidence commit: `81d440f818342d75c28218d7e940c4fb55fd9691`;
- `artifacts/SHA256SUMS` SHA-256:
  `4b9246ce18edf12bb74a158bf0f3de62dca45e0c94fa64158290f7a675bb6fef`.

## Evidence

- [`research/audits/short-leaf-double-hit/REPORT.md`](research/audits/short-leaf-double-hit/REPORT.md)
- [`src/phase31_short_leaf_search.py`](src/phase31_short_leaf_search.py)
- [`verifier/verify_phase31_short_leaf.py`](verifier/verify_phase31_short_leaf.py)
- [`research/experiments/phase31-short-leaf-double-hit.json`](research/experiments/phase31-short-leaf-double-hit.json)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

## What this result does not prove

It does not provide the resonant resultant, exclude positive cycles, audit the
H89 `q0` candidates, close any nonperiodic branch, or prove Collatz.
