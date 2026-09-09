# Phase 43 — normalization-barrier run results

Date: 2026-09-10. Base: `04727b5d3d10b33a9cadb0d316fd218871a38817`.
Branch: `feat/phase43-normalization-barrier`. `proves_collatz=false`.

## Outcome

P257--P261 are the audited normalization barrier, finite rational
all-length/all-Q certificate, minimizer-specific completeness, auxiliary
13S bound and endpoint-to-prefix propagation. Full proofs and source
provenance are in the [`audit`](research/audits/normalization-barrier/REPORT.md).
The supplied [`proposal`](research/audits/normalization-barrier/PROPOSAL.md)
is retained separately; its assertions are not acceptance inputs.

| Independent result | Value |
|---|---:|
| Queries: S=1..127,L=0..20 plus (703,80) | 2,668 |
| Certified no strict improvement, all lengths/Q | 185 |
| Actual positive literal improvements | 2,483 |
| Maximum candidate source | 705 |
| Forward-closed reference states | 1,189 |
| Nonclosed (703,80) potential states | 1,188 |
| Newly reconstructed capacity rows N=0..48 | 49 |
| Mandatory-family rows / retained named controls | 61 / 22 |
| Certified finite defect-drop queries in this domain | 21 |

NG46 improves the supplied finite falsifier: the least source/length is
**(7,4)**, `7 -> 11 -> 17 -> 26 -> 13`, whose odd defect decreases 1->0.
Its all-prefix all-length coefficient maximality is certified. The
minimality proof checks the safety boundary of sources below 7; it is not
inferred merely from the finite grid.

The supplied (703,80) control remains valid: endpoint 1256, Q=51,
`a_43=6>a_44=2`, transition `50165 --e=5--> 4703`. Its certificate covers
all 81 prefixes including length zero. The set is not forward closed:
5024 is listed but 2512 is not; the default potential covers the open exit.
The generator reports 254 normalization cuts and 451 endpoint-omitting
cycles. Those counters are diagnostics, not mathematical acceptance inputs.

## Reproduce

From the repository root, with the existing development environment:

```bash
.venv/bin/python src/phase43_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase43.py --artifact-dir artifacts --output artifacts/phase43_verifier.json
.venv/bin/python -m pytest -q tests/test_phase43_properties.py tests/test_phase43_verifier.py tests/test_research_health.py
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
```

Use a clean acceptance worktree for the final strict check. To query a
single target without changing accepted evidence:

```bash
.venv/bin/python src/phase43_search.py --source 7 --length 4 --output /tmp/collatz-phase43-example.json
.venv/bin/python verifier/verify_phase43.py --certificate /tmp/collatz-phase43-example.json
.venv/bin/python src/phase43_search.py --source 703 --length 80 --maximum-work 1
```

The last command returns `UNKNOWN`; the independent checker rejects it as
a certificate. The old `src/phase41_search.py` length-bounded mode and its
historical artifacts are unchanged.

## Independence, dependencies and verification scope

The generator follows candidate orbits and solves finite stopped graphs.
The verifier reconstructs literal affine maps by positional sums and checks
potential inequalities directly, without importing or running barrier search.
A separate reverse traversal of an independently checked forward-closed
graph supplies complete first-hit coefficient comparisons; all observed
cycles contract. Thus all-length acceptance does not rely on search's cutoff.

P260 reuses the accepted E46 convergence certificate (including E28) and
E54's shell-49 tail. Five inherited artifacts are hash-pinned. Only N<=48
capacities and the new rational logarithm comparisons enter the new Phase 43
artifact set. Dependency tests also rerun the existing Phase 38 capacity
generator through N=500 and its scalar tail comparison; this is not a full
independent rerun of E54's other evidence. **The full E46/E54 computations
are not rerun**. No external X02 is used.

- New properties, certificate/tamper, input and CLI tests: **98 passed**
  in 3.04s before control-plane integration.
- Dependency regression: **190 passed** in 27.65s, covering Phase 41 and
  Phase 42 properties/verifiers plus Phase 38 properties.
- Final clean-worktree acceptance and provenance are recorded below after
  the implementation commit; the entire repository suite is not claimed.

One intermediate formal-model regression rejected an over-restricted
square-index lag formula in the development verifier. The full exact
square/b_j condition was restored and checked. No old evidence was changed
to make the new implementation pass. A stronger, smaller NG46 falsifier was
retained rather than limiting the report to the supplied 703 example.

## Artifact map and SHA-256

- [`phase43_queries.json`](artifacts/phase43_queries.json): every certificate
  or witness, plus the exact finite monotonicity-obstruction list.
- [`phase43_certificate_703.json`](artifacts/phase43_certificate_703.json):
  independently usable all-length endpoint certificate.
- [`phase43_certificate_7.json`](artifacts/phase43_certificate_7.json):
  the small, independently usable minimal NG46 certificate.
- [`phase43_reference.json`](artifacts/phase43_reference.json): reachable
  forward-closed comparison graph.
- [`phase43_capacity.json`](artifacts/phase43_capacity.json): N<=48 rows,
  rational 13S comparisons and inherited hashes.
- [`phase43_regressions.json`](artifacts/phase43_regressions.json): mandatory
  families, named obstructions, formal/ordinary and positive/negative controls.
- [`phase43_verifier.json`](artifacts/phase43_verifier.json): independent results.
- [`SHA256SUMS`](artifacts/SHA256SUMS): tracked generated-evidence manifest.

The implementation commit and manifest hash are recorded in the
[`experiment`](research/experiments/phase43-normalization-barrier.json) once
clean-worktree acceptance is complete. This two-commit procedure avoids a
self-referential commit/hash field in generated evidence.

## What this result does not prove

Arbitrary-target search termination, an effective last join, uniform
certificate size, a contradicting defect-variation budget, and infinite
geodesic monotonicity are not established. P259 actually guarantees that a
hypothetical global minimizer has a finite certificate at every prefix;
producing certificates alone cannot exclude it. NG46 concerns finite paths,
not an infinite counterexample. H112/H72/H89/H133 and positive cycles remain
unresolved. The Collatz conjecture is not proved or disproved.
