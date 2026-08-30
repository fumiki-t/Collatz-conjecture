# Phase 23 run results — defect area and factor separation

Status: accepted exact derivations and bounded computations; the Collatz
conjecture remains `OPEN`; `proves_collatz=false`.

## Result

The supplied proposal contained a finite-boundary error.  The smallest exact
counterexample is `q=4`, `c_q=1101100`, `n=2`, `A=0`: the factor set has four
members, not at most `n+1=3`.  NG32 records this failure.

The repaired critical bound is

\[
p_w(n)\le(A(w)+1)(n+1)+1,
\]

and, under P54 plus pairwise-distinct critical states,

\[
K_q\le A(w)(n_q+2)+2n_q+1.
\]

For coprime cycle profiles, Phase 23 proves the literal adjacent-swap area,
`A>=h(h+1)/2`, cyclic factor complexity, and the primitive-positive-cycle
necessary condition `L<=(A+1)(n_cyc+1)`.  Polynomial critical height and
cycle-minimum consequences remain explicitly conditional.

## Exact finite scope

- 502,523 critical words through `q<=17`;
- 31 area-only rejections;
- 82,227 direct factor checks through `q<=12`;
- 3,579 union rejections through `q<=12`, with zero Phase-23-only additions
  beyond P132;
- 4,786 coprime cycle profiles of area at most two through `q<=22`;
- 156,178 cyclic factor checks;
- 2,214 complete cyclic classes through `q<=8`; only the trivial cycle and
  its powers are integral.

## Reproduction

```bash
.venv/bin/python src/phase23_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase23.py \
  --artifact-dir artifacts --write-report artifacts/phase23_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase23_properties.py tests/test_phase23_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

The generator completed with `valid=true`; the independent verifier completed
with `valid=true`, `generator_imported=false`, and `proves_collatz=false`.
Final test counts, commit provenance, and manifest SHA-256 are recorded in the
accepted experiment manifest.

## Evidence

- [`research/audits/defect-area/REPORT.md`](research/audits/defect-area/REPORT.md)
- `artifacts/phase23_theory.json`
- `artifacts/phase23_critical_words.json`
- `artifacts/phase23_cycle_profiles.json`
- `artifacts/phase23_regressions.json`
- `artifacts/phase23_obstruction_report.md`
- `artifacts/phase23_verifier.json`
- `artifacts/SHA256SUMS`

## What this result does not prove

It does not certify the proposed giant `q0` area number, prove H89 or H133,
exclude all nontrivial cycles, eliminate H112/H72, or prove the Collatz
conjecture. `proves_collatz=false`.
