# Phase 15 surplus-dominance provenance

## Base and untrusted input

- Base: `origin/main` at
  `a246c97200df61030b0c6874cbf150fd9b152f0c`.
- Branch: `feat/phase15-surplus-dominance`.
- The supplied note was treated as an untrusted specification, not evidence.
- Supplied-note SHA-256:

```text
88bb79325a090b4c1d9643bddc0be23352668da03cb946a58fffb7ffce0721ac  phase15_surplus_dominance_note.md
```

Existing untracked `scratch/` and artifact files were preserved and are not
part of Phase 15 acceptance evidence.

## Independent reconstruction

- Generator: `src/phase15_search.py`, using packed immutable safe-word rows and
  incremental exact affine constants.
- Verifier: `verifier/verify_phase15.py`, using literal-string tuple rows and
  independently reconstructed constants, residues, and traces.
- The verifier contains none of `phase15_search`, `from src`, or `import src`.
- Both enumerate all safe words and dominance classes through Q=17, but the
  arbitrary-target valley pass reconstructs all combination words separately.
- Tamper tests mutate theorem, frontier, valley, gap-decoder, and adversarial
  artifacts and require rejection.

## Acceptance boundary

P86--P88 are accepted only with the quantifiers written in the proof report.
E24 is finite through Q=17.  H72 and nontrivial cycles remain open, and
`proves_collatz=false`.

## Commands and results

```bash
.venv/bin/python src/phase15_search.py \
  --artifact-dir artifacts --max-q 17
.venv/bin/python verifier/verify_phase15.py \
  --artifact-dir artifacts --output artifacts/phase15_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase15_properties.py tests/test_phase15_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
```

```text
generator Q<=17:             completed in 180.89s
independent verifier Q<=17:  valid=true in 191.83s
focused Phase 15 suite:      14 passed in 4.46s
complete repository suite:   237 passed in 276.69s
P86/P87/P88=VERIFIED_THEOREM
E24=VERIFIED_FINITE
NG25/NG26=REFUTED
H72=OPEN
proves_collatz=false
global artifacts/SHA256SUMS SHA-256:
fa7d3dc8ceb6c48e7ab570fb6a6f09c9a5ca70908542389f23095ec56088114a
```
