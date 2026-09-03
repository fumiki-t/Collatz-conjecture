# Phase 35 results — full decoder and corrected joint scalar sieve

The untrusted proposal was independently reconstructed on
`feat/phase35-full-decoder-joint-scalar`. The complete modular decoder is
valid, and the joint cycle inequalities raise the accepted critical area floor
from `A>=209` to `A>=229`. The proposed `A>=238` derivation is refuted by an
exact scalar tuple. `proves_collatz=false`.

## Accepted claims

- `P206 VERIFIED_THEOREM`: branch-free full defect decoding on the valid
  critical-safe image, including exact endpoint displacement.
- `P207 VERIFIED_THEOREM`: exact finite P179 factor-count corollary.
- `P208 VERIFIED_THEOREM`: exact residual-area sharpening of P195.
- `P209 VERIFIED_THEOREM`: a least-state/profile mismatch produces a strictly
  better smaller-denominator upper approximation.
- `P210 VERIFIED_THEOREM`: every critical primitive positive nontrivial
  integer cycle has reduced-profile area `A>=229`.
- `E49 VERIFIED_FINITE`: all 1,166,058 critical-safe words through `q=18`
  pass independent full-decoder and endpoint reconstruction.
- `E50 VERIFIED_FINITE`: exact cutoff, CF frontier, and 7,221-row joint scalar
  audit.
- `NG41 REFUTED`: the stated Phase 35 scalar sieve proves `A>=238`.

`H89`, `H133`, and `H172` remain `OPEN`.

## Exact obstruction

The first joint scalar survivor is

```text
(q,L,A,h,J,Sigma,E,n,Z)=(2301,3647,229,2,138,90,92,24,10)
P207 margin=10
P208 margin=43
```

It is not asserted to be a realizable positive cycle. It shows exactly why
the proposed area-238 conclusion is not licensed by the stated inequalities.

## Reproduction

```text
.venv/bin/python src/phase35_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase35.py --artifact-dir artifacts --output artifacts/phase35_verifier.json
.venv/bin/python -m pytest -q tests/test_phase35_properties.py tests/test_phase35_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/research_health.py --strict
cd artifacts && shasum -a 256 -c SHA256SUMS
```

Acceptance evidence so far:

- focused Phase 35 and health suite: `14 passed in 265.16s`;
- full repository suite: `480 passed in 2925.14s`;
- implementation commit: `c3d1e5fb4a3a936ebef1292aaf4e90c0810f1fc1`;
- evidence-manifest commit: `ecc2d048a64da6456c1753336c9885023b847950`;
- `artifacts/SHA256SUMS` SHA-256:
  `b8b285520a9422355fef710b5f0982acce5a82e5c1a5cd360adee01b9cfa0708`.
- strict research health: `valid=true`, no errors or warnings, 239 tracked
  artifacts; complete SHA-256 manifest verification passed.

## Evidence

- [`research/audits/full-decoder-joint-scalar/REPORT.md`](research/audits/full-decoder-joint-scalar/REPORT.md)
- [`src/phase35_search.py`](src/phase35_search.py)
- [`verifier/verify_phase35.py`](verifier/verify_phase35.py)
- [`research/experiments/phase35-full-decoder-joint-scalar.json`](research/experiments/phase35-full-decoder-joint-scalar.json)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

## What this result does not prove

The full decoder is not a smaller-ancestor construction. The area floor does
not exclude area 229 or arbitrary-area cycles, and no nonperiodic branch is
closed. The Collatz conjecture remains open.
