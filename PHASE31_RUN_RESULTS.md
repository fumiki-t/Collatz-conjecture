# Phase 31 run results — double-hit transport

Phase 31 was independently audited on `feat/phase31-double-hit` from the
accepted Phase 30 `main`. Static extraction and the stronger area constant
are valid after repairing the proposed global near-grid interpretation.
`proves_collatz=false`.

## Accepted claims

- `P185 VERIFIED_THEOREM`: static singleton extraction and `E<=h+Sigma`.
- `P186 VERIFIED_THEOREM`: residual-context, low-hit, and double-hit factor
  inequalities.
- `P187 VERIFIED_THEOREM`: the stronger slope-dependent area constant.
- `P188 VERIFIED_THEOREM`: exact noncritical and EXT17-dependent critical
  constants.
- `P189 VERIFIED_THEOREM`: repaired near-equality structure, local relative
  to the residual exceptional set.
- `P190 VERIFIED_THEOREM`: exact and approximate grid identities.
- `E43 VERIFIED_FINITE`: independent corpus, synthetic, scalar, and
  regression reconstruction.
- `NG40 REFUTED`: area equality alone does not force global near-grid
  invariance.

`H172` and `H133` remain `OPEN`.

## Reproduction

```text
.venv/bin/python src/phase31_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase31.py --artifact-dir artifacts --output artifacts/phase31_verifier.json
.venv/bin/python -m pytest -q tests/test_phase31_properties.py tests/test_phase31_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/research_health.py --strict
shasum -a 256 -c artifacts/SHA256SUMS
```

Final test results, evidence commit, and manifest hash are recorded in the
accepted experiment manifest.

## Evidence

- [`research/audits/double-hit-transport/REPORT.md`](research/audits/double-hit-transport/REPORT.md)
- [`src/phase31_search.py`](src/phase31_search.py)
- [`verifier/verify_phase31.py`](verifier/verify_phase31.py)
- [`research/experiments/phase31-double-hit-transport.json`](research/experiments/phase31-double-hit-transport.json)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

## What this result does not prove

The stronger necessary area growth and conditional grid identity do not
exclude arbitrary-area cycles. The grid-like/residual-heavy arithmetic
dichotomy required by H172 remains open, as do all nonperiodic obligations
and the Collatz conjecture.
