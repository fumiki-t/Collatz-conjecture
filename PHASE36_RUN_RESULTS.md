# Phase 36 results — root intervals and the positive event polynomial

The untrusted proposal was independently reconstructed on
`feat/phase36-root-event-polynomial`.  The cycle-root and positive-event
lemmas are valid, and the exact Phase 35 area-229 scalar obstruction is not a
realizable cycle profile.  The accepted critical area floor rises from
`A>=229` to `A>=230`.  Direct cycle-root reuse for the P206 decoder is false;
the corrected mirror intervals are recorded separately.  The Collatz
conjecture remains open and `proves_collatz=false`.

## Accepted claims

- `P211 VERIFIED_THEOREM`: cycle root localization plus exact factor/gap
  bounds.
- `P212 VERIFIED_THEOREM`: bounded-root one-hit capacity inequality.
- `P213 VERIFIED_THEOREM`: the exact NG41 area-229 scalar tuple is not a
  realizable primitive positive cycle profile.
- `P214 VERIFIED_THEOREM`: every critical primitive positive nontrivial
  integer cycle has reduced-profile area `A>=230`.
- `P215 VERIFIED_THEOREM`: shifted positive Mersenne recurrence and period
  divisor identity.
- `P216 VERIFIED_THEOREM`: coprime positive event-polynomial coefficients,
  support, norm, and modular equivalence.
- `P217 VERIFIED_THEOREM`: exact positive-event sparse-arc inequalities.
- `P218 VERIFIED_THEOREM`: corrected mirror-root localization for P206
  decoder profiles.
- `E51/E52 VERIFIED_FINITE`: independent bounded cycle/event, scalar, and
  decoder audits.
- `NG42 REFUTED`: direct reuse of cycle-root intervals for the decoder.

`H89`, `H133`, and `H172` remain `OPEN`.

## Exact boundary values

```text
area-229 upper-convergent multiples: 1926
area-229 low-q rows:                 7221
sole scalar survivor:               (2301,3647,229,2,138,90,92,24,10)
root capacity:                       6017 < 2L=7294 (margin -1277)
cycle classes q<=8:                 2214
coprime event classes q<=8:          797
decoder words q<=18:             1166058
smallest decoder orientation failure: q=3
```

## Reproduction

```text
.venv/bin/python src/phase36_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase36.py --artifact-dir artifacts --output artifacts/phase36_verifier.json
.venv/bin/python -m pytest -q tests/test_phase36_properties.py tests/test_phase36_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/research_health.py --strict
cd artifacts && shasum -a 256 -c SHA256SUMS
```

Acceptance evidence:

- focused Phase 36 and health suite: `16 passed in 204.79s`;
- full repository suite: `491 passed in 2280.05s`;
- implementation commit: `30b5fed2d4cfd91cadf4cc1c735411eb2ddf3a7d`;
- evidence-manifest commit: `3095b7ffc6750aae179a5a7e2b4a8a7363351344`;
- `artifacts/SHA256SUMS` SHA-256:
  `ecf0e5b76b2127e6b4911bf8f8297e2186ebd460bba231417160084bf49d17e9`;
- strict research health: `valid=true`, no errors or warnings, 247 tracked
  artifacts; complete SHA-256 manifest verification passed.

## Evidence

- [`research/audits/root-event-polynomial/REPORT.md`](research/audits/root-event-polynomial/REPORT.md)
- [`src/phase36_search.py`](src/phase36_search.py)
- [`verifier/verify_phase36.py`](verifier/verify_phase36.py)
- [`research/experiments/phase36-root-event-polynomial.json`](research/experiments/phase36-root-event-polynomial.json)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

## What this result does not prove

The area floor does not exclude area 230 or arbitrary area.  Root/event
structure does not yet form a complete dichotomy, and decoder mirror
localization is not an ancestor theorem.  No periodic or nonperiodic branch
is fully excluded.  The Collatz conjecture remains open.
