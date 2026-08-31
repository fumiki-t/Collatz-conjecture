# Phase 29 run results — automatic arc nonvanishing

Phase 29 was independently audited on `feat/phase29-arc-nonvanishing` from the
latest accepted Phase 28 `main`.  The proposal's coprime arc-nonvanishing
argument is valid, while the arbitrary-area and noncoprime cycle problems
remain open.  `proves_collatz=false`.

## Accepted claims

- `P173 VERIFIED_THEOREM`: every P147 coprime circular arc is nonzero, with an
  exact 2-adic valuation from its unique least transport weight.
- `P174 VERIFIED_THEOREM`: exact critical and noncritical resonance
  inequalities.
- `P175 VERIFIED_THEOREM`: every fixed defect area admits only finitely many
  coprime primitive positive-cycle profiles; the critical part uses EXT17.
- `P176 VERIFIED_THEOREM`: an all-gcd reduced-slope maximum-state bound.
- `P177 VERIFIED_THEOREM`: every primitive positive nontrivial integer cycle
  has reduced odd period at least 971, using internally verified E28.
- `P178 CONDITIONAL`: the lower bound becomes 72,057,431,991 assuming X02.
- `E41 VERIFIED_FINITE`: exact bounded reconstruction and adversarial audit.

`H172` and `H133` remain `OPEN`.

## Reproduction

```text
.venv/bin/python src/phase29_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase29.py --artifact-dir artifacts --output artifacts/phase29_verifier.json
.venv/bin/python -m pytest -q tests/test_phase29_properties.py tests/test_phase29_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/research_health.py --strict
sha256sum -c artifacts/SHA256SUMS
```

## Exact finite result

The independent verifier accepted all 93,629 tied-largest-gap arc cuts and
reconstructed 797 coprime classes, five synthetic profiles, 5,615 all-gcd
maximum-state rows, both Farey boxes, and every mandatory adversarial family.
The focused Phase 29 property/verifier suite initially passed 14 tests in
99.60 seconds; final repository-wide counts are recorded in the experiment
manifest after acceptance.

## Evidence

- proof audit: [`research/audits/arc-nonvanishing/REPORT.md`](research/audits/arc-nonvanishing/REPORT.md)
- generator: [`src/phase29_search.py`](src/phase29_search.py)
- independent verifier: [`verifier/verify_phase29.py`](verifier/verify_phase29.py)
- artifacts: `artifacts/phase29_*`
- experiment contract: [`research/experiments/phase29-arc-nonvanishing.json`](research/experiments/phase29-arc-nonvanishing.json)
- SHA-256 manifest: [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

## What this result does not prove

Automatic nonvanishing does not control coefficient growth at unbounded area,
does not supply a full-`D` noncoprime obstruction, and does not eliminate
cycles or nonperiodic Collatz orbits.  The Collatz conjecture remains open.
