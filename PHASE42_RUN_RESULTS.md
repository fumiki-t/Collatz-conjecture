# Phase 42 — mechanical capacity and the square-root model's ordinary source

Base: `098251967ee347ce9847a10c08ffc303bf21c48a` (Phase 41 acceptance).
Branch: `feat/phase42-mechanical-capacity`.
The supplied September 9 followup was independently audited against current
main, not adopted as an authority. Exact proofs, quantifiers, provenance and
corrections are in the [`complete audit`](research/audits/mechanical-capacity/REPORT.md).

## Results and boundaries

- P252 gives simultaneous mechanical-interval capacity and integrated energy
  for positive, distinct, literal coefficient-safe prefixes.
- P253 bounds maximum defect together with downward variation. Its general
  asymptotic corollary uses internal P221; it permits oscillating survivors.
- P254 proves `liminf a_q/sqrt(q)>=sqrt(2 log_2 3)` when the defect is
  nondecreasing. It does not prove that actual geodesics have that property.
- P255 consequently excludes a positive ordinary infinite source for the
  specific Phase 13 square-root word u and P251's `w=110111111u`.
  Their formal/2-adic existence and NG45's analytic-only no-go remain valid.
- P256 establishes the exact minimum `q=22` for negative same-q carry,
  preserving NG28's old q=26 witness and P88's two-sided `{1,2}` boundary.

No Garcia--Tal, Heppner, X02 or other new external theorem is needed for the
monotone result or this specific source exclusion. The argument uses ordinary
integer parity separation, not a real-versus-2-adic contradiction.

## Independently reconstructed finite evidence

| Component | Exact scope / result |
|---|---|
| Ordinary orbit conventions | 2,048 odd sources in [1,4095]; at most 300 odd steps, stopping before coefficient failure or repetition |
| Interval arithmetic | 5,069 odd steps, 4,304 pure intervals, 30,060 levels |
| Important limitation | Zero counted n-factors in that ordinary sample: CAP is vacuous there, not strong finite packing evidence |
| Complete negative-carry exclusion | q=2..20 extremal inequalities; 12 q=21 patterns and all 48 possible remaining cases rejected |
| Attaining witness | q=22, sources 29023002619 and 14511501311; endpoint 53013941237; carry -3 |
| Nonvacuous repeat certificates | Eight source bounds `S<=2^B`, B=8,16,32,64,128,256,512,1024, for u |
| Largest repeat certificate | Full prefix 391,004; starts 386,295 and 389,455; common prefix 1,548 bits; tested width 1,543 |
| Regressions | Six required families, 24 parameterized sources, 80 distinct words, NG28/32/43, source167/source7 and cycle controls |

The repeat verifier checks a literal later split and two exact affine height
bounds. It does not need an infinite/nonperiodic assumption. Source bounds
refer to u, not to the preceding finite extension w. The all-source exclusion
uses P254's written asymptotic proof, never extrapolation from these bounds.

## Reproduction and independence

From the repository root:

```sh
.venv/bin/python src/phase42_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase42.py --artifact-dir artifacts --output artifacts/phase42_verifier.json
.venv/bin/python -m pytest -q tests/test_phase42_properties.py tests/test_phase42_verifier.py tests/test_research_health.py
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
```

Use a fresh temporary directory as `--artifact-dir` in the first two commands
for an isolated reproduction and compare the five `phase42_*.json` files.
Verify all accepted artifact hashes from `artifacts/` with
`shasum -a 256 -c SHA256SUMS`.

The verifier imports no generator. It uses full shortcut trajectories rather
than accelerated construction, segmentwise deletion rather than run-boundary
construction, positional correction sums and forced-source forward decoding
rather than the leading-bit decoder, and a closed square-index formula rather
than the formal model's recurrence. Its repeat acceptance is a direct finite
certificate check. All decisions are integer/rational; altered scopes, omitted
cases, changed hypotheses, malformed JSON and tampered arithmetic are rejected.

Acceptance execution details and immutable commit/hash references are recorded
in the [`experiment contract`](research/experiments/phase42-mechanical-capacity.json).
The original untracked scratch directory is preserved and not published.
Old Phase 41 accepted artifacts remain byte-for-byte unchanged: their then-open
ordinary-source annotation is historical, superseded for this model by P255.

## What this result does not prove

H112/H72/H89/H133 remain `OPEN`; `proves_collatz=false`. General defects
need not be monotone, faster monotone growth remains possible, and downward
variation may satisfy P253. No theorem yet turns ancestral minimality or
canonical lifts into a contradicting defect/variation budget. Negative-carry
minimality is not eventual ancestor existence. Positive cycles remain separate.
