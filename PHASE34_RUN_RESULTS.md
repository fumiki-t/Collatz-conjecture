# Phase 34 results — least-state/profile bridge and critical area 209

The untrusted proposal was independently reconstructed on
`feat/phase34-profile-state-area209`. The audited result raises the critical
reduced-profile floor from `A>=118` to `A>=209` and adds an exact first step
for a 2-adic source-defect decoder. `proves_collatz=false`.

## Accepted claims

- `P202 VERIFIED_THEOREM`: at a least odd cycle state, `h<=a_t+1`, without
  identifying the least-value and discrepancy-minimum rotations.
- `P203 VERIFIED_THEOREM`: exact exponential-moment and strict integer
  profile bounds for the actual least state.
- `P204 VERIFIED_THEOREM`: every critical primitive positive nontrivial
  integer cycle has reduced-profile area `A>=209`.
- `P205 VERIFIED_THEOREM`: the 2-adic valuation of a source-residue defect
  identifies the first edited odd position and its gap-two unit edit.
- `E48 VERIFIED_FINITE`: independent exact reconstruction of the declared
  scalar, rational-profile, and defect corpora.

`H89`, `H133`, and `H172` remain `OPEN`.

## Exact audit summary

The high-`q` audit reconstructs nine upper convergents and 1,725 candidate
multiples below `10^13`; all fail. The low-`q` audit reconstructs 7,221 rows:
1,216 fail the reduced-period floor, 5,979 fail the state/E46 bound, 26 reach
P195, and none survives at area 208.

The first obstruction is `(q,L,A)=(2301,3647,209)`, with P195 margin 24 and
least-state interval `[583561,860946]`. No new trajectory computation was used.

The verifier separately checks 10,103 positive critical rational rotations
through `q<=12` and 21,766 legal 2-adic defect profiles through `q<=18`.

## Reproduction

```text
.venv/bin/python src/phase34_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase34.py --artifact-dir artifacts --output artifacts/phase34_verifier.json
.venv/bin/python -m pytest -q tests/test_phase34_properties.py tests/test_phase34_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/research_health.py --strict
cd artifacts && shasum -a 256 -c SHA256SUMS
```

Acceptance timing, commits, and manifest hash are recorded after the final
clean-worktree acceptance run.

## Evidence

- [`research/audits/profile-state-area209/REPORT.md`](research/audits/profile-state-area209/REPORT.md)
- [`src/phase34_search.py`](src/phase34_search.py)
- [`verifier/verify_phase34.py`](verifier/verify_phase34.py)
- [`research/experiments/phase34-profile-state-area209.json`](research/experiments/phase34-profile-state-area209.json)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

## What this result does not prove

The finite area floor and first-defect identity do not exclude arbitrary-area
cycles, produce a complete defect decoder, address nonperiodic branches, or
prove the Collatz conjecture.
