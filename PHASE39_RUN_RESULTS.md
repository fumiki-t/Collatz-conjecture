# Phase 39 — macroscopic carry and jump geodesics

Base: `cb31e7960c1fa593d3b96b4259ae22d513a3d13e` (Phase 38 acceptance).
Branch: `feat/phase39-macroscopic-carry-jump-geodesic`.
Proposal: `phase39_macroscopic_carry_jump_geodesic.md`, SHA-256
`6721f48193f40c725e3519f2ff10faec38c3cfcf2f7503d3687fd48156664519`.
The proposal is an unaudited input; accepted statements are in the ledger and
the [`proof audit`](research/audits/macroscopic-carry-jump-geodesic/REPORT.md).

## Results and repaired scope

- P235--P237: exact current-state carry for nonnegative k,s, eventual failure
  of fixed distinct direct lifts, and necessary shortening `k>=Q-O(1)` when
  local odd counts are subexponential in Q. The latter strengthens the
  proposal's `Q-o(Q)` bound under the same explicit hypotheses.
- P238: exact shifted-correction DAG and positive source jump, retaining
  full safety after adjusting the initial run. The universal r>=4 family
  begins with `111100` from 15 and `11101` from 7, both ending at 20.
- P239: renewal-boundary occupancy `<2X^(29/30)` for every integer X>=1.
- P240 `CONDITIONAL`: under X02, P228/E54 implies `Y_infinity<2S`, so a least
  permanent-safe nonperiodic source is all-prefix same-Q geodesic. H112
  would contradict P115's eventual zero lifts. H112 remains `OPEN`.
- P241: exact positive integer event direction and positive-cycle count
  `M>m log(1/lambda)`; noncritical cycles give `M>m log 2`.

The identity rewrite survives every prefix. The nonidentity pair
`a=1,d=101,S=1` has zero carry on the trivial cycle. P236 therefore has
explicit distinctness and nonperiodicity assumptions. Its conclusion does
not prohibit growing compositions or every use of finite dictionaries.
The rational fixed point x=1/5,e=3 shows why the event-direction equality
claim needs ordinary integer positivity. The reciprocal sum in P240 includes
its initial odd source, and least-source selection is across all eligible
positive orbits. No new external theorem is introduced.

## Exact finite evidence

| Audit | Scope and result |
|---|---|
| Carry | 51 safe words of length <=8, 172 relations, 127 prefixes of length <=6, 21,844 rows; 6,391 carry passes, 93 safe positive descents, 570 nonzero dominant bounds |
| Jump DAG | All 4,095 paths and 1,938 vertices through ell=12; ell counts the first zero, so the residual suffix has length <=11; initial run R<=12 |
| Jump candidates | 10,520 pairs; all safe in this finite scope; maximum observed gain 3 |
| First gain 2 | ell=8,R=10, tails `1000001` -> `1011100`, source 183295 -> 45823 |
| First gain 3 | ell=8,R=12, tails `0000001` -> `1011100`, source 593919 -> 74239 |
| Boundary capacity | 500 exact binomial rows and exact integer entropy inequalities |
| Positive endpoint bridge | 8,178 words through length12 containing a 1; 24,534 literal positive lifts |
| Cycle/event checks | 1,320 positive rational exponent-word rows q<=5,e<=4; 32,768 actual accelerated transitions from odd starts 1..1023 |

The first-gain ordering is ell, initial run, original tail lexicographic,
alternative tail lexicographic. Rational/repeated cycle words are not new
primitive positive integer cycles. The absence of unsafe DAG candidates is
finite evidence only; the safety check remains required at arbitrary depth.

## Independence and reproduction

The generator propagates affine B, constructs the DAG forward, and computes
canonical residues by modular inversion. The verifier independently expands
B at odd positions, groups complete binary tails by their closed-form J,
uses parity-bit lifting for source residues, and reconstructs capacities
with Pascal rows and cycles with rotated fixed points. It imports no search
implementation and recomputes every row digest. Separate agents also audited
the mathematical proofs; neither source separation nor agent separation is
treated as a formal proof certificate for the infinite statements.

```bash
.venv/bin/python src/phase39_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase39.py \
  --artifact-dir artifacts --output artifacts/phase39_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase39_properties.py tests/test_phase39_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q \
  tests/test_phase15b_properties.py tests/test_phase16_properties.py \
  tests/test_phase19_properties.py tests/test_phase37_properties.py \
  tests/test_phase38_properties.py tests/test_phase38_verifier.py
.venv/bin/python verifier/verify_phase38.py \
  --artifact-dir artifacts --output /tmp/collatz_phase39_dependency_verifier.json
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

Verification results and acceptance commit are recorded in
[`the experiment manifest`](research/experiments/phase39-macroscopic-carry-jump-geodesic.json).
Phase 39 properties, verifier/tamper tests, and control-plane tests: **61
passed in 22.76s**. Directly used dependency tests: **33 passed in 118.03s**.
The independent Phase 38 certificate rerun also returned `valid=true`.
The initial control-plane run exposed two stale Phase 38 field assertions;
they were updated for Phase 39 and the full focused set was rerun successfully.
Strict research health returned `valid=true`, no errors or warnings, and
265 tracked artifact entries. Markdown links were valid across 147 files.
The test scope covers the new code, control plane, and directly used earlier
properties/certificates; a new whole-repository test run is not claimed.
The previous Phase 38 run of 515 tests remains historical evidence only.

## Evidence and SHA-256

SHA-256 of `artifacts/SHA256SUMS`:
`b629ea2ca612051a68282bf96fa44a36868d2d111eae6664bf863c0f9da4450b`.

- [`carry`](artifacts/phase39_carry_audit.json)
- [`jump DAG`](artifacts/phase39_jump_dag.json)
- [`capacity and cycles`](artifacts/phase39_capacity_cycle.json)
- [`regressions`](artifacts/phase39_regressions.json)
- [`obstruction report`](artifacts/phase39_obstruction_report.md)
- [`independent verifier result`](artifacts/phase39_verifier.json)
- [`SHA-256 manifest`](artifacts/SHA256SUMS)

## What this result does not prove

H112, H72, H133 and the Collatz conjecture remain open. There is no all-depth
ancestor construction, DAG confluence, unconditional nonperiodic exclusion,
internal finite exhaustion below 2^49, or arbitrary-area critical-cycle
exclusion. X02 remains external evidence. `proves_collatz=false`.
