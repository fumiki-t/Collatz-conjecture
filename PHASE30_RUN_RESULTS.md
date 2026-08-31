# Phase 30 run results — direct token transport

Phase 30 was independently audited on `feat/phase30-direct-transport` from
the accepted Phase 29 `main`. The direct transport and sharper area constant
are valid after repairing one unsupported state-saturation sentence.
`proves_collatz=false`.

## Accepted claims

- `P179 VERIFIED_THEOREM`: direct factor-set transport with the exact span.
- `P180 VERIFIED_THEOREM`: sharpened all-gcd positive-cycle separation.
- `P181 VERIFIED_THEOREM`: the improved slope-dependent area constant.
- `P182 VERIFIED_THEOREM`: exact noncritical and critical constants; only the
  critical specialization uses EXT17.
- `P183 VERIFIED_THEOREM`: repaired near-equality rigidity, without claiming
  actual maximum-state saturation.
- `P184 VERIFIED_THEOREM`: singleton-transport normal form with secondary
  peaks charged to exact descent slack.
- `E42 VERIFIED_FINITE`: independent corpus, synthetic, scalar, and regression
  reconstruction.
- `NG39 REFUTED`: the span-free factor bound fails at `(q,L,n)=(6,10,4)`.

`H172` and `H133` remain `OPEN`.

## Reproduction

```text
.venv/bin/python src/phase30_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase30.py --artifact-dir artifacts --output artifacts/phase30_verifier.json
.venv/bin/python -m pytest -q tests/test_phase30_properties.py tests/test_phase30_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/research_health.py --strict
sha256sum -c artifacts/SHA256SUMS
```

The final focused suite passed 20 tests in 18.68 seconds. The full repository
suite passed 423 tests in 1422.59 seconds, and strict research health returned
`valid=true` with no errors or warnings. The accepted evidence commit is
`32d8973af1eb5f043a5627de8d2c5eb3fec3a6cd`; the SHA-256 of the artifact
manifest at that commit is
`6dfbb56420b4f5860b4b3ad942d4459425fbb464eeb711290d5860d2b128224c`.

## Evidence

- [`research/audits/direct-transport/REPORT.md`](research/audits/direct-transport/REPORT.md)
- [`src/phase30_search.py`](src/phase30_search.py)
- [`verifier/verify_phase30.py`](verifier/verify_phase30.py)
- [`research/experiments/phase30-direct-transport.json`](research/experiments/phase30-direct-transport.json)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

## What this result does not prove

The sharper necessary area growth does not exclude arbitrary-area cycles.
The pair-aware subleading resonance theorem required by H172 remains open,
as do all nonperiodic obligations and the Collatz conjecture.
