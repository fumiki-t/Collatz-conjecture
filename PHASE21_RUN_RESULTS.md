# Phase 21: repetition-complexity barriers — run results

Branch: `feat/phase21-repetition-complexity`

Base: `f4a9b6818fad5d406f6d4db9785a98cc830f8b82`

Repository status: `OPEN`; `proves_collatz=false`.

## Accepted scope

The supplied note was audited as an untrusted proposal.  Proofs, corrections,
and dependency boundaries are in
[`research/audits/repetition-complexity/REPORT.md`](research/audits/repetition-complexity/REPORT.md).

| Claim | Status | Accepted statement |
|---|---|---|
| EXT14 | `EXTERNAL_THEOREM` | Bernstein--Lagarias parity conjugacy is literature context; P125 is rederived internally. |
| P125 | `VERIFIED_THEOREM` | Distinct integer parity tails have LCP exactly `v2(a-b)`. |
| P126 | `VERIFIED_THEOREM` | A repeated factor at second start `j` obeys the strict exact height inequality. |
| P127 | `VERIFIED_THEOREM` | Positive nonperiodic integer parity words have `liminf p(n)/n >= 1/log2(3/2)`. |
| P128 | `CONDITIONAL` | EXT08 raises the necessary `limsup` slope to `log(3)/log(3/2)`. |
| P129/P130 | `VERIFIED_THEOREM` | `Dio(v)<=log2(3)` and prefix powers have exact source-height bounds. |
| P131 | `VERIFIED_THEOREM` | Factor complexity and finite orbit peak obey the exact residue-capacity tradeoff. |
| P132 | `VERIFIED_THEOREM` | Repetition gives an exact finite H89 rejection certificate. |
| E33 | `VERIFIED_FINITE` | 299,999 direct sources, 502,523 critical words, 406,353 geodesic words, and 132 adversarial rows were independently rebuilt. |
| H89/H112/H72 | `OPEN` | No eventual repeat or repeat-to-lift theorem is proved. |

## Finite results

- Direct sources: `1<=N<300000` (299,999 sources).
- Repeat widths: all `1<=n<=64`, covered by each second start's maximal LCP.
- Maximum distinct states: 279 at source 230631.
- Maximum state: 12,324,038,948 at source 270271.
- Maximum distinct-state LCP: 20 at source 33019.
- Critical words through Q=17: 502,523; P132 rejects 160,429.
- Same-Q geodesic words through Q=17: 406,353; P132 rejects 120,982.
- At Q=17: 32,524/312,455 critical and 21,462/253,018 geodesic words are rejected.
- Controls: 11 named 512-bit words and 132 mandatory-family rows.

The large surviving complement is the exact obstruction: repetition alone is
not yet an eventual H89 mechanism.

## Reproduction

```bash
.venv/bin/python src/phase21_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase21.py \
  --artifact-dir artifacts --write-report artifacts/phase21_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase21_properties.py tests/test_phase21_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

Observed acceptance-bound computations before documentation acceptance:

- generator: `valid=true` in `391.22s` wall time;
- independent verifier: `valid=true` in `899.63s` wall time;
- property/tamper tests: `12 passed in 0.64s`;
- focused Phase 21/control-plane tests: `17 passed in 6.83s`;
- full repository suite: `311 passed in 666.58s`;
- strict research health: `valid=true`, 140 tracked artifacts, no warnings;
- SHA-256 manifest: `f2e6634beeef6f36b706431de93898946d064e331ce578f4e092d00ccfa07ab2`;
- independent result: `proves_collatz=false`.

Final full-suite, strict-health, commit, and manifest provenance are recorded
in `research/experiments/phase21-repetition-complexity.json`.

## Tamper rejection

Tests reject:

- replacing the strict repeat-height inequality by a weak inequality;
- omitting the non-eventually-periodic/state-distinct exception;
- substituting `h(i)` for `h(j)`;
- changing the critical `log2(3/2)` coefficient;
- setting `proves_collatz=true`.

## What this result does not prove

- A linear symbolic-complexity lower bound is not an orbit-height upper bound.
- The finite Q<=17 rejection rate is not an eventual theorem.
- H89, H112, H72, nontrivial cycles, and the Collatz conjecture remain open.
- `proves_collatz=false`.
