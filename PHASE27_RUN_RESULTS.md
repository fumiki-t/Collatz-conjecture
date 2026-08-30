# Phase 27 run results — asymptotic cycle area and support

**Date:** 2026-08-30
**Branch:** `feat/phase27-asymptotic-cycle-area`
**Repository status:** `OPEN`
**`proves_collatz=false`**

The supplied note was audited as a proposal.  Its polynomial-gap reduction,
internal noncritical gap, Matveev specialization, and arbitrary-gcd support
bound survive exact audit.  A proposed implicit rotation identification does
not: NG36 preserves its smallest positive rational obstruction.

## Accepted results

- `EXT17 EXTERNAL_THEOREM`: Matveev's explicit real logarithmic-form bound.
- `P162 VERIFIED_THEOREM`: a polynomial multiplier gap forces
  `liminf A_*/q^(2/3)>=((log_2 3)^2/2)^(1/3)`.
- `P163 VERIFIED_THEOREM`: the noncritical branch has an internal polynomial
  gap.
- `P164 VERIFIED_THEOREM`: EXT17 supplies the critical gap, so P162 applies
  globally to hypothetical positive-cycle sequences.
- `P165 VERIFIED_THEOREM`: arbitrary-gcd defect support satisfies the Hamming,
  factor, height, and asymptotic `sqrt(q)` bounds.
- `E39 VERIFIED_FINITE`: exact corpus, envelope, synthetic-profile, and
  adversarial reconstruction.
- `NG36 REFUTED`: least-value and discrepancy-minimum rotations need not agree
  for positive rational affine cycles.
- `H133 OPEN`: neither asymptotic dispersion bound excludes all cycles.

## Exact finite evidence

- cyclic exponent classes through `q<=8`: `2214`;
- primitive / critical / noncritical: `2186 / 204 / 2010`;
- noncoprime classes: `1417`;
- support Hamming and height checks: `3101` each;
- support factor checks: `45369`;
- exact synthetic tall/diffuse profiles: `8`;
- mandatory adversarial rows: `7`.

The smallest rotation mismatch is the primitive positive rational shadow

```text
e=(1,3): 5/7 -> 11/7 -> 5/7
least-value offset = 0
discrepancy-minimum offset = 1
```

It is not an integer cycle.

## Independence and tamper rejection

The verifier does not import `src/phase27_search.py`.  It independently uses
recursive reverse compositions, integer-encoded cyclic factors, direct exact
rational traces, 84-term logarithm boxes, and separate profile synthesis.
Tests reject altered corpus digests, the Matveev majorant, promotion of EXT17,
rotation-obstruction fields, and `proves_collatz=true`.

## Reproduction

```bash
.venv/bin/python src/phase27_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase27.py \
  --artifact-dir artifacts --output artifacts/phase27_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase27_properties.py tests/test_phase27_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
.venv/bin/python scripts/research_health.py --strict
git diff --check
```

The accepted evidence is fixed at commit
`dd8de1ef2ead68f7b90454370842748da6f13833`. The focused suite reports
`18 passed in 180.19s`; the complete repository suite reports
`380 passed in 1293.65s`. Strict research health reports `valid=true` with
178 tracked artifacts and no errors, warnings, or untracked artifacts. The
SHA-256 of the accepted `artifacts/SHA256SUMS` is
`e4b0606333a3a610e995e52aa9e55f06b3616955160fe8c8d6be4e099ed5c876`.

## What this result does not prove

Phase 27 does not exclude arbitrary-area positive cycles, either structural
profile branch, nonperiodic counterexamples, or the Collatz conjecture.
`proves_collatz=false`.
