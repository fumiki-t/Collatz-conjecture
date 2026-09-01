# Phase 32 results — triple-hit capacity and full-cofactor rigidity

The Phase 32 note was independently audited on
`feat/phase32-triple-hit-cofactor`.  P195--P199 survive in their stated exact
domains.  The proposed `d=s=6` eventual exclusion lacks an effective identity
classification and is retained as H200 OPEN. `proves_collatz=false`.

## Accepted claims

- `P195 VERIFIED_THEOREM`: exact finite triple-hit factor inequality.
- `P196 VERIFIED_THEOREM`: optimized area constant, with noncritical cube
  `4725/64` and EXT17-dependent critical enclosure `(4.430667,4.430668)`.
- `P197 VERIFIED_THEOREM`: full reduced-block decomposition and `M_d|Delta`
  necessity.
- `P198 VERIFIED_THEOREM`: primitive positive integral block corrections
  oscillate by at least `R=2^L0`.
- `P199 VERIFIED_THEOREM`: positive support-arc divisor and critical area-six
  reduction `d<=s<=6`.
- `E45 VERIFIED_FINITE`: independent `q<=9` triple-hit/cofactor reconstruction.

`H200`, `H172`, and `H133` remain `OPEN`.

## Reproduction

```text
.venv/bin/python src/phase32_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase32.py --artifact-dir artifacts --output artifacts/phase32_verifier.json
.venv/bin/python -m pytest -q tests/test_phase32_properties.py tests/test_phase32_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/research_health.py --strict
cd artifacts && shasum -a 256 -c SHA256SUMS
```

Acceptance evidence:

- focused suite: `14 passed in 42.25s`;
- full suite: `456 passed in 1715.66s`;
- strict research health: `valid=true`, no errors or warnings;
- evidence commit: `0ea676bb2a6cea5f554de4252e13a4d969330614`;
- `artifacts/SHA256SUMS` SHA-256:
  `61d88f7db436d97f1396d6de0bead60cc7204f440550acd0d498133e8d74511d`.

## Evidence

- [`research/audits/triple-hit-cofactor/REPORT.md`](research/audits/triple-hit-cofactor/REPORT.md)
- [`src/phase32_search.py`](src/phase32_search.py)
- [`verifier/verify_phase32.py`](verifier/verify_phase32.py)
- [`research/experiments/phase32-triple-hit-cofactor.json`](research/experiments/phase32-triple-hit-cofactor.json)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

## What this result does not prove

It does not exclude any complete area-six gcd class, arbitrary-area cycles,
either nonperiodic branch, or Collatz.
