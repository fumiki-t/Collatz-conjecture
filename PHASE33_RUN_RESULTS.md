# Phase 33 results — critical-area bootstrap

The untrusted Phase 33 proposal was independently reconstructed on
`feat/phase33-critical-area-bootstrap`.  The two exact bootstrap tiers survive:
every critical primitive positive nontrivial integer cycle must have area
`A>=118`.  The finite convergence input was independently extended to every
positive start below `583561`.  `proves_collatz=false`.

## Accepted claims

- `P200 VERIFIED_THEOREM`: every critical primitive positive nontrivial cycle
  has reduced-profile area `A>=62`.
- `P201 VERIFIED_THEOREM`: with E46, the lower bound strengthens to `A>=118`.
- `E46 VERIFIED_FINITE`: E28 plus 141,780 independently reconstructed
  first-descent rows prove convergence for every positive start `n<583561`.
- `E47 VERIFIED_FINITE`: exact cutoff, CF-frontier, and low-`q` reconstruction;
  the two CF frontiers contain 461 and 915 rows.
- `H200 RETRACTED`: its method-specific bounded-grid obligation is no longer
  active because P201 closes the `A=s=d=6` target by a stronger route. The
  classifier itself was not completed.

`H172` and `H133` remain `OPEN`.

## Exact audit summary

The area-61 low-`q` audit covers 1,077 values: 405 fail `q0>=971`, 669
conflict with P133/E28, and none of the three remaining rows satisfies P195.
The closest row is `(q,L)=(971,1539)`, where `RHS-3L=-3`.

The area-117 audit covers 3,125 values: 808 reduced-denominator rejections,
2,305 P133/E28 rejections, 12 admissible rows, and one P195 survivor at
`q=971`.  E46 rejects that survivor.  The closest other row is `q=1636`, with
margin `-21`.  At area 118 it becomes the next scalar obstruction, with margin
45.

The descent certificate covers every odd source from 300001 through 583559.
The first subinterval has maximum first-descent time 121 at 303103, reaching
208055; the second has maximum 173 at 381727, reaching 323434.

## Reproduction

```text
.venv/bin/python src/phase33_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase33.py --artifact-dir artifacts --output artifacts/phase33_verifier.json
.venv/bin/python -m pytest -q tests/test_phase33_properties.py tests/test_phase33_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/research_health.py --strict
cd artifacts && shasum -a 256 -c SHA256SUMS
```

Acceptance counts, commit IDs, and the manifest hash are recorded after the
clean acceptance run in the experiment manifest.

## Evidence

- [`research/audits/critical-area-bootstrap/REPORT.md`](research/audits/critical-area-bootstrap/REPORT.md)
- [`src/phase33_search.py`](src/phase33_search.py)
- [`verifier/verify_phase33.py`](verifier/verify_phase33.py)
- [`research/experiments/phase33-critical-area-bootstrap.json`](research/experiments/phase33-critical-area-bootstrap.json)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

## What this result does not prove

A finite area lower bound does not exclude arbitrary-area or noncritical
positive cycles, either nonperiodic branch, or the Collatz conjecture.
