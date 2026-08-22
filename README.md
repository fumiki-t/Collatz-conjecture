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

Phases 1–6 provide exact finite searches and independent verification. The
strongest current result is a `CONDITIONAL` Phase 6 reduction, supplemented by
`VERIFIED_FINITE` barrier certificates. Bounded searches, high coverage, and
external datasets are never promoted to asymptotic claims.

Current status: [`docs/STATUS.md`](docs/STATUS.md)  
Ten-minute handoff: [`docs/HANDOFF.md`](docs/HANDOFF.md)

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
.venv/bin/python verifier/verify_phase6.py \
  --artifact-dir artifacts \
  --output /tmp/collatz_phase6_verifier.json
shasum -a 256 artifacts/SHA256SUMS
```

The final command should report
`1f7d1b4c564a01c9af7ea82abaa949df3444ed757bfc09faad00a526e2487653`.
The verifier output path is outside `artifacts/` so a reproduction check does
not overwrite committed evidence.

## Repository guide

- [`docs/INDEX.md`](docs/INDEX.md): canonical documentation map.
- [`RESEARCH_HISTORY.md`](RESEARCH_HISTORY.md): chronological Phase 1–6 record.
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

Acceptance records:

- [Phase 1–2](RUN_RESULTS.md)
- [Phase 3](PHASE3_RUN_RESULTS.md)
- [Phase 4](PHASE4_RUN_RESULTS.md)
- [Phase 5](PHASE5_RUN_RESULTS.md)
- [Phase 6](PHASE6_RUN_RESULTS.md)
- [SHA-256 manifest](artifacts/SHA256SUMS)

## Important disclaimer

`OPEN` certificate nodes are unresolved. `VERIFIED_FINITE` means only the
stated bounded domain was exhausted. `EXTERNAL_THEOREM` and
`EXTERNAL_EVIDENCE` are not internally reproved. Any claimed proof or
disproof must follow the emergency audit protocol in [`AGENTS.md`](AGENTS.md).
