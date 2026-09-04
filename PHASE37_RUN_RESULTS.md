# Phase 37 run results — internal uniform sparsity

## Outcome

Phase 37 was implemented and independently audited on branch
`feat/phase37-internal-uniform-sparsity` from Phase 36 acceptance commit
`22e39664ef6bb7fcc110b78d2faa00b85d6947e4`.

The supplied v2 note replaced the earlier draft and was treated as an
untrusted proposal. Its central recursion is valid after making the required
choice `rho_*<rho<1` explicit in the reciprocal, companion-limit, and cycle
applications.

- P219--P226 are `VERIFIED_THEOREM`.
- E53 is `VERIFIED_FINITE`.
- H70, H72, H133, and the Collatz conjecture remain `OPEN`.
- `proves_collatz=false`.

The main exact conclusion is

\[
G(X)=O_\rho(X^\rho)
\quad\left(\rho>H_2(1/\log_2 3)\right),
\]

for every equal-time collision-free positive set and every translated integer
interval. The rational specialization is fully explicit:

\[
\boxed{G(X)<32X^{29/30}}\qquad(X\ge1).
\]

The exact induction threshold is `N0=135`; the low-part inequality fails at
`N=134` and succeeds at 135.

## Mathematical consequences

P221/P222 prove internally that every non-eventually-periodic positive
shortcut orbit has a convergent reciprocal sum, discrepancy tending to
`+infinity`, and an odd permanent coefficient-safe suffix minimum. Therefore
the surviving global alternatives are:

1. a nontrivial positive cycle;
2. a permanent-safe nonperiodic positive tail.

This removes EXT07/P74 as a necessary dependency for that ordinary Collatz
reduction. The external theorem and its conditional consequences remain valid
historical records. H70 is not marked proved; its standalone spacing statement
has instead become unnecessary for the global nonperiodic dichotomy.

P223 gives

\[
\#\{j:a_j\le A\}=O(2^{\rho A})
\]

for every `rho>rho_*`, together with summable defects and every density-one
coefficient `c<1/rho_*`. P224/P225 prove `h_i=o(S_i)` and
`limsup S_(i+1)/S_i<=3/2`. P226 makes every noncritical primitive positive
cycle minimum effectively bounded, but no optimized cutoff or finite
exhaustion is claimed.

## Exact finite audit

The generator and the implementation-independent verifier reconstruct:

- 131,070 complete parity words through `N<=16`;
- 152 fixed-weight affine extrema and unique parity residues;
- 49,928 points in 180 translated intervals through `N<=12`, including
  translations above `2^200`;
- 854 fixed-weight translated image groups;
- 209,868 exact affine/product steps from starts through 4096;
- 154 first-upcrossing words through length 16;
- 84 finite renewal addresses and 228 strict suffix-minimum boundaries;
- 154 exact positive/companion block transitions;
- all mandatory adversarial families, source 167, and trivial and negative
  cycle controls.

The rational-shadow and P206/P218 orientation distinctions are retained as
documented scope boundaries rather than being misreported as new finite
recomputations.

These bounded computations audit conventions; the uniform theorem is the
strong-induction proof in the detailed report.

## Reproduction

```bash
.venv/bin/python src/phase37_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase37.py \
  --artifact-dir artifacts --output artifacts/phase37_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase37_properties.py \
  tests/test_phase37_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

The initial focused Phase 37 property/tamper suite passed `12` tests. Final
acceptance-suite counts are recorded in the experiment manifest after the
full run.

## Artifacts and SHA-256

| Artifact | SHA-256 |
|---|---|
| `phase37_affine_interval_audit.json` | `7f043bd929b1c7ba99290abe091a462513dee3d3e694d18c7049235371d16f4a` |
| `phase37_induction_certificate.json` | `c829e6787be13c36f3bb73b935193cfc6e08c1f17c8b9bcc7642f26abf1283de` |
| `phase37_obstruction_report.md` | `bcfb0c637035d02c4df4e749b28d8d2a0638c56032d9bd00f3dd35a80e52dfde` |
| `phase37_regressions.json` | `8139886fa42c244b39dd402ba7a29ef27f94b1e7f8261fdeb45e5df72513579d` |
| `phase37_renewal_audit.json` | `f57df2dca75cac01143db98c8fe118d9126622483f9448db63df6b29e0c9717c` |
| `phase37_theory.json` | `6dcbb3e28402eed0623eb9cc4918620b63f4be28e0a59cf55985cdb092da37e0` |
| `phase37_verifier.json` | `27a97573c6815c70d8a17edbf4ddb41c0187e10798924708586a128c37832516` |

The complete `artifacts/SHA256SUMS` manifest has SHA-256
`bc4f59fb1c0cfa86dc4c1173ae4db5e0d8ecaecac6507c30cbcb5697a6f7ba5e`.

## What this result does not prove

Uniform sparsity applies to one equal-time collision-free set. It does not
control multiplicity across many canonical renewal addresses and therefore
does not prove either P80 anti-concentration premise. The defect conclusion is
density-one rather than pointwise; the companion and endpoint bounds allow an
infinite path. No permanent-safe positive source, critical cycle, or
arbitrary-area cycle is excluded.

This phase does not prove or disprove the Collatz conjecture.
`proves_collatz=false`.
