# Collatz conjecture research archive

This repository records an exact-computation research program for the shortcut
Collatz map

\[
T(n)=\begin{cases}
n/2,&n\equiv0\pmod2,\\
(3n+1)/2,&n\equiv1\pmod2.
\end{cases}
\]

The objective is the original Collatz conjecture. The repository preserves
successful finite certificates, independent verifiers, failed approaches, and
open proof obligations so that the work can be audited and continued.

## Research status

**`OPEN` — this repository has not proved or disproved the Collatz
conjecture.**

Phases 1–12 provide exact finite searches, symbolic lemmas, independent
verification, and preserved failures. The strongest route remains the
`CONDITIONAL` Phase 6 reduction. Phases 7–10 localize its first possible large
crossing, reduce the endpoint to one gap residue, derive a renewal barrier, and
split every positive q0 near-gap pair into 30 first-divergence cases. P68 adds
an exact finite-horizon two-tail state; NG19 preserves explicit counterexamples
to every shorter residue window at horizon 12. Phase 11 gives the full
counterexample trichotomy and a dropping-safe renewal-ladder barrier. Phase 12
adds an odd-orbit packing theorem for its infinite-safe-tail branch and rules
out the single all-contact mechanical word, but does not eliminate that branch
or the cycle alternative. C04, C05, H54, H70, and H72 remain open. Bounded searches, high
coverage, and external inputs are never promoted to asymptotic claims.

Current status: [`docs/STATUS.md`](docs/STATUS.md)

Ten-minute handoff: [`docs/HANDOFF.md`](docs/HANDOFF.md)

AI continuation guide: [`docs/AI_RESEARCH_GUIDE.md`](docs/AI_RESEARCH_GUIDE.md)

## Current strongest route

Let `M(k)` be the least positive integer whose first `k` shortcut prefixes all
satisfy `3^{q_j} >= 2^j`. For `K_q = ceil(q log_2 3)`, Phase 6 independently
checks the conditional implication

\[
M(K_q-1)\le N\le H_q
\]

for a least positive counterexample `N` whose coefficient first crosses below
one at that barrier. Consequently, proving

\[
M(K_q-1)>H_q
\]

for all sufficiently large `q`, followed by finite verification of the
remaining cases, would close this route. The missing eventual lower bound for
`M(k)` is the main bottleneck; it is not established here.

## Reproduction

Python 3.12 or later is required. The complete acceptance commands and hashes
are in the phase result files. A code/test verification from the repository
root is:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python verifier/verify_phase10.py \
  --artifact-dir artifacts --output /tmp/collatz_phase10_verifier.json
.venv/bin/python verifier/verify_branch_point.py \
  --artifact-dir artifacts --output /tmp/collatz_branch_verifier.json
.venv/bin/python verifier/verify_two_tail.py \
  --artifact-dir artifacts --output /tmp/collatz_two_tail_verifier.json
.venv/bin/python verifier/verify_phase11.py \
  --artifact-dir artifacts --output /tmp/collatz_phase11_verifier.json
.venv/bin/python verifier/verify_phase12.py \
  --artifact-dir artifacts --output /tmp/collatz_phase12_verifier.json
.venv/bin/python scripts/research_health.py
shasum -a 256 artifacts/SHA256SUMS
```

The expected manifest hash is recorded in
[`PHASE12_RUN_RESULTS.md`](PHASE12_RUN_RESULTS.md).
The verifier output path is outside `artifacts/` so a reproduction check does
not overwrite committed evidence.

## Repository guide

- [`docs/INDEX.md`](docs/INDEX.md): canonical documentation map.
- [`docs/AI_RESEARCH_GUIDE.md`](docs/AI_RESEARCH_GUIDE.md): active dependency
  graph, exact next experiments, known traps, and AI completion checklist.
- [`research/registry.json`](research/registry.json): machine-readable current
  acceptance boundary, active obligations, dependencies, and context packs.
- [`research/claims-index.json`](research/claims-index.json): generated JSON
  projection of all claim rows for AI retrieval; the Markdown ledger remains
  canonical.
- [`research/README.md`](research/README.md): experiment-contract and AI
  control-plane conventions.
- [`RESEARCH_HISTORY.md`](RESEARCH_HISTORY.md): chronological Phase 1–12 record.
- [`docs/CLAIMS_LEDGER.md`](docs/CLAIMS_LEDGER.md): claim IDs, statuses,
  dependencies, evidence, and counterexamples.
- [`docs/FAILED_APPROACHES.md`](docs/FAILED_APPROACHES.md): approaches that
  should not be retried without a new mechanism.
- [`docs/LITERATURE.md`](docs/LITERATURE.md): annotated primary literature.
- [`docs/ROADMAP.md`](docs/ROADMAP.md): ranked proof-oriented research program.
- [`AGENTS.md`](AGENTS.md): mandatory protocol for human and AI contributors.
- `src/`: search/generator implementations.
- `verifier/`: logically separate certificate verifiers.
- `tests/`: exact arithmetic, tamper rejection, and adversarial regressions.
- `artifacts/`: generated evidence; do not edit it manually.

GitHub pull requests and pushes to `main` run a lightweight integrity gate.
The full acceptance suite is available as a manually dispatched workflow so
large finite checks do not consume resources on every documentation edit.

Acceptance records:

- [Phase 1–2](RUN_RESULTS.md)
- [Phase 3](PHASE3_RUN_RESULTS.md)
- [Phase 4](PHASE4_RUN_RESULTS.md)
- [Phase 5](PHASE5_RUN_RESULTS.md)
- [Phase 6](PHASE6_RUN_RESULTS.md)
- [Phase 7](PHASE7_RUN_RESULTS.md)
- [Phase 8](PHASE8_RUN_RESULTS.md)
- [Phase 9](PHASE9_RUN_RESULTS.md)
- [Phase 10](PHASE10_RUN_RESULTS.md)
- [Branch-point supplement](BRANCH_POINT_RUN_RESULTS.md)
- [Two-tail supplement](TWO_TAIL_RUN_RESULTS.md)
- [Phase 11](PHASE11_RUN_RESULTS.md)
- [Phase 12](PHASE12_RUN_RESULTS.md)
- [SHA-256 manifest](artifacts/SHA256SUMS)

## Important disclaimer

`OPEN` certificate nodes are unresolved. `VERIFIED_FINITE` means only the
stated bounded domain was exhausted. `EXTERNAL_THEOREM` and
`EXTERNAL_EVIDENCE` are not internally reproved. Any claimed proof or
disproof must follow the emergency audit protocol in [`AGENTS.md`](AGENTS.md).
