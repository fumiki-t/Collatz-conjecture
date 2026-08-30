# Phase 28 run results — transport dispersion

**Date:** 2026-08-30
**Branch:** `feat/phase28-transport-dispersion`
**Repository status:** `OPEN`
**`proves_collatz=false`**

The supplied note was audited as a proposal.  Its transport, level-set,
sharp-optimization, branch-constant, and rigidity mechanisms survive after an
endpoint repair.  Two overstrong finite statements fail and their smallest
exact obstructions are preserved as NG37 and NG38.

## Accepted results

- `P166 VERIFIED_THEOREM`: exact balanced `J`-insertion/`J`-deletion
  transport and factor/state separation.
- `P167 VERIFIED_THEOREM`: `J=sum U_k`, `A=sum |I_k|`, and the exact
  descent-density lower bound.
- `P168 VERIFIED_THEOREM`: the sharp transport-area constant
  `C(ell)=3 ell^(2/3)/(2^(5/3)(ell-1)^(1/3))`.
- `P169 VERIFIED_THEOREM`: internal noncritical constant `3/2` and critical
  constant in `(1.535941,1.535942)`, with EXT17 retained explicitly.
- `P170 VERIFIED_THEOREM`: unique near-extremal height/transport scaling and
  saturation requirements.
- `P171 VERIFIED_THEOREM`: exact multilevel endpoint decomposition, support
  at most `2J+1`, and the corrected `l1` estimate.
- `E40 VERIFIED_FINITE`: independent finite, synthetic, and adversarial
  reconstruction.
- `NG37 REFUTED`: the new descent bound is not strictly better for every
  finite nonzero profile.
- `NG38 REFUTED`: the endpoint-free multilevel `l1` bound is false.
- `H172 OPEN`, `H133 OPEN`: no all-area cycle exclusion follows.

## Exact finite evidence

- cyclic exponent classes through `q<=8`: `2214`;
- primitive / noncoprime classes: `2186 / 1417`;
- discrepancy-minimum rotations: `3101`;
- density interval checks: `179606`;
- cyclic factor checks: `45369`;
- transport and polynomial checks: `3101` each;
- exact synthetic profiles: `5`;
- mandatory adversarial families: `7`.

The two proposal obstructions are:

```text
NG37: q=3, L=5, e=(3,1,1), profile=(0,1,0,0), old=new=1
NG38: q=2, L=4, e=(3,1),   profile=(0,1,0),   Q_a=(3,-1), 4>3
```

## Independence and tamper rejection

The independent verifier does not import the generator.  It reconstructs the
corpus by reverse compositions and uses direct boundary subtraction, integer
factor encodings, transition-count level sets, independent synthetic
recurrences, and an 88-term logarithm enclosure.  Tests reject mutations of
the corpus digest, critical constant, EXT17 dependency, endpoint correction,
NG37 witness, and `proves_collatz` field.

## Reproduction

```bash
.venv/bin/python src/phase28_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase28.py \
  --artifact-dir artifacts --output artifacts/phase28_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase28_properties.py tests/test_phase28_verifier.py \
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
`82b8e3b7169ba18298efdb4f2ff38f10efd2a9bc`. The focused suite reports
`19 passed in 26.46s`; the complete repository suite reports
`394 passed in 1315.58s`. Strict research health reports `valid=true` with
185 tracked artifacts and no errors, warnings, or untracked artifacts. The
SHA-256 of the accepted `artifacts/SHA256SUMS` is
`305542986c9c56a366e17b47ee0edffd18055f42226d649274507d48fd40267f`.

## What this result does not prove

Phase 28 does not exclude arbitrary-area positive cycles or either
nonperiodic counterexample branch.  H172 and H133 remain open.  It does not
prove or disprove the Collatz conjecture.  `proves_collatz=false`.
