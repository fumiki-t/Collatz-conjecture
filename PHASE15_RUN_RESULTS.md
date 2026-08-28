# Phase 15: surplus-dominating ancestors — run results

Branch: `feat/phase15-surplus-dominance`

Base commit: `a246c97200df61030b0c6874cbf150fd9b152f0c`

Phase 15 proves the surplus-dominance least-source principle, the exact
strict-valley suffix reduction, and finite endpoint injectivity for `{1,2}`
odd-gap words. It independently exhausts the cross-Q dominance frontier
through `Q<=17`. It does not prove an eventual frontier theorem, H72, or the
Collatz conjecture.

The detailed proof and quantifiers are in
[`research/audits/surplus-dominance/REPORT.md`](research/audits/surplus-dominance/REPORT.md).

## Accepted results

- P86 `VERIFIED_THEOREM`: a least positive permanent-safe
  discrepancy-escaping source has no smaller safe coalescent ancestor with at
  least the prefix's terminal coefficient surplus.
- P87 `VERIFIED_THEOREM`: an unsafe shorter coalescent target has a unique
  strict-valley safe suffix; positivity, literal coalescence, and source
  descent are checked separately.
- P88 `VERIFIED_THEOREM`: at every fixed finite Q, the endpoint residue is
  injective on odd-gap exponent words in `{1,2}`.
- E24 `VERIFIED_FINITE`: complete target/competitor and valley enumeration
  through Q=17, plus mandatory adversarial regression.
- NG25 `REFUTED`: same-Q safe targets are not a complete dominance language.
- NG26 `REFUTED`: unsafe targets cannot be discarded before valley extraction.
- H72 remains `OPEN`; `proves_collatz=false`.

## Principal finite results

| Q | safe words | same-Q dominated | Qb<=Q dominated | Qb<=17 dominated |
|---:|---:|---:|---:|---:|
| 4 | 7 | 1 | 1 | 2 |
| 5 | 12 | 2 | 2 | 8 |
| 6 | 30 | 6 | 10 | 24 |
| 7 | 85 | 18 | 39 | 70 |
| 8 | 173 | 36 | 72 | 127 |
| 9 | 476 | 98 | 234 | 358 |
| 10 | 961 | 193 | 417 | 690 |
| 11 | 2,652 | 524 | 1,306 | 1,953 |
| 12 | 8,045 | 1,581 | 4,419 | 6,086 |
| 13 | 17,637 | 3,428 | 8,704 | 12,919 |
| 14 | 51,033 | 9,841 | 27,739 | 38,173 |
| 15 | 108,950 | 20,793 | 53,041 | 77,839 |
| 16 | 312,455 | 59,191 | 167,037 | 215,667 |
| 17 | 663,535 | 124,513 | 320,168 | 320,168 |

The explicit finite cutoff is essential. At target Q=17, the `Qb<=17` and
`Qb<=Qd` columns coincide only because no higher competitor layer was
enumerated.

The least named cross-Q witness is

```text
d=111110100: (Q,L,B,S,Y)=(6,9,697,287,410)
b=1:         (Q,L,B,V,Y)=(1,1,1,273,410)
3/2 > 729/512.
```

The unsafe-target enumeration finds no additional reduction through Q=14,
then exactly 12, 90, and 233 at Q=15,16,17 beyond same-Q safe targets. The
named Q=15 strict-valley suffix maps 527131 to the same endpoint 3205946 as
the safe target from 1874247.

At Q=17, 32,596 safe `{1,2}`-gap words have pairwise distinct endpoint
residues and none is dominated by a competitor with `Qb<=Qd`. This is a
finite hard core, not an infinite obstruction theorem.

## Reproduction

```bash
.venv/bin/python src/phase15_search.py \
  --artifact-dir artifacts --max-q 17
.venv/bin/python verifier/verify_phase15.py \
  --artifact-dir artifacts --output artifacts/phase15_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase15_properties.py tests/test_phase15_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

The verifier contains none of `phase15_search`, `from src`, or `import src`.
Tamper tests mutate theorem, frontier, valley, gap-core, and adversarial
artifacts and require rejection.

Acceptance checks:

```text
generator Q<=17:             completed in 180.89s
independent verifier Q<=17:  valid=true in 191.83s
focused Phase 15 suite:      14 passed in 4.46s
complete repository suite:   237 passed in 276.69s
global artifact manifest SHA-256:
fa7d3dc8ceb6c48e7ab570fb6a6f09c9a5ca70908542389f23095ec56088114a
```

## What this result does not prove

- eventual extinction or persistence of the surplus-undominated frontier;
- that a cutoff survivor has no higher-Q dominator;
- either P80 canonical-representative anti-concentration estimate;
- H72 or exclusion of a positive permanent-safe tail;
- exclusion of nontrivial cycles;
- the Collatz conjecture.

`proves_collatz=false`.
