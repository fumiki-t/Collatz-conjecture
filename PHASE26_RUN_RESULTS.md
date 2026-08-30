# Phase 26 run results — reduced-slope cycle-area barrier

**Date:** 2026-08-30
**Branch:** `feat/phase26-cycle-area-barrier`
**Repository status:** `OPEN`
**`proves_collatz=false`**

The supplied Phase 26 note was audited as a proposal.  Its reduced-slope
profile, arbitrary-slope factor separation, critical area-six lower frontier,
and conservative noncritical barrier survive exact audit.  The sharper private
constant was not promoted because it adds no present strategic closure.

## Accepted claims

- `P156 VERIFIED_THEOREM`: reduced-slope time profile, literal edit area,
  cyclic factor bound, and triangular height bound for arbitrary gcd.
- `P157 VERIFIED_THEOREM`: arbitrary-slope positive-cycle height and factor
  separation.
- `P158 VERIFIED_THEOREM`: every critical primitive positive nontrivial cycle
  has `A_*>=6`.
- `P159 VERIFIED_THEOREM`: every noncritical primitive positive nontrivial
  cycle has `A_*>100000`.
- `P160 CONDITIONAL`: assuming X02, the noncritical bound becomes
  `A_*>5*10^15`.
- `P161 VERIFIED_THEOREM`: exact noncritical slope/area phase inequality.
- `E38 VERIFIED_FINITE`: complete structural audit through `q<=8`.
- `NG35 REFUTED`: EXT05 plus scalar factor separation cannot also exclude
  critical area six.
- `H147 VERIFIED_THEOREM`: the former area-three obligation is closed in the
  positive-cycle scope by the stronger P158 barrier.
- `H133 OPEN`: arbitrary-area cycle exclusion remains unsolved.

## Exact finite evidence

- positive-D cyclic exponent classes: `2214`;
- primitive classes: `2186`;
- noncoprime classes: `1417`;
- minimum-height rotations: `3101`;
- cyclic factor-width checks: `45369`;
- critical small-q scalar rows: `511`;
- passing critical small-q rows: `0`.

The first exact method obstruction is

```text
75^7 = 13348388671875
3*64^7 = 13194139533312
```

so the critical proof's exponential margin reverses at area six.  This is not
an area-six cycle.

## Independence and tamper rejection

The verifier does not import `src/phase26_search.py`.  It independently uses
recursive composition enumeration, ordered-one displacement, direct rational
traces, exact integer scans, and a separately coded atanh logarithm enclosure.
Tests reject altered profile digests, scalar margins, conditional promotion,
and `proves_collatz=true`.

## Reproduction

```bash
.venv/bin/python src/phase26_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase26.py \
  --artifact-dir artifacts --output artifacts/phase26_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase26_properties.py tests/test_phase26_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
.venv/bin/python scripts/research_health.py --strict
git diff --check
```

Acceptance commit, final test totals, strict-health result, and manifest hash
are recorded in `research/experiments/phase26-cycle-area-barrier.json` after
the clean acceptance run.

## What this result does not prove

Phase 26 does not eliminate critical area six or above, arbitrary-area
positive cycles, any nonperiodic counterexample branch, or the Collatz
conjecture. `proves_collatz=false`.
