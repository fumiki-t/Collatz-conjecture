# Collatz conjecture research archive

This repository is an exact-arithmetic research program for the shortcut
Collatz map

\[
T(n)=
\begin{cases}
n/2,&n\text{ even},\\
(3n+1)/2,&n\text{ odd}.
\end{cases}
\]

Its objective is to prove or disprove the original Collatz conjecture. The
repository preserves proofs and conditional reductions, independent
verifiers, finite certificates, external dependencies, counterexamples to
failed approaches, and open obligations so future researchers do not need the
original chat history.

## Status

**`OPEN` — this repository has not proved or disproved the Collatz
conjecture. `proves_collatz=false`.**

Phase 17 is the latest accepted research layer. It proves exact r<=4
predecessor exclusions, an exponent-code pressure identity, and a
suffix-decodable finite code. It splits every distinct-odd-value finite first
crossing into G270 (all-prefix same-Q geodesic) or H270
(`N<q/270`, `X<q/135`, `Z<2q/135`). Neither branch is excluded. NG29 records
a precise ceiling for coefficient-only summed-Haar pressure; E28/E29 are
finite. H54, H70, H72, H89, H104, H105, C03, C04, C05, the periodic/nontrivial-cycle branch, and the
permanent-safe-tail branch remain open.

Start with the [research synthesis](docs/RESEARCH_SYNTHESIS.md). It defines the
map and conventions, summarizes Phases 1–17, separates internal and external
results, records failed mechanisms, and states the remaining proof obligations.

Canonical status and navigation:

- [research synthesis](docs/RESEARCH_SYNTHESIS.md)
- [current status](docs/STATUS.md)
- [claims ledger](docs/CLAIMS_LEDGER.md)
- [proof-oriented roadmap](docs/ROADMAP.md)
- [ten-minute handoff](docs/HANDOFF.md)
- [AI research guide](docs/AI_RESEARCH_GUIDE.md)
- [failed approaches](docs/FAILED_APPROACHES.md)
- [annotated literature](docs/LITERATURE.md)
- [machine-readable registry](research/registry.json)

The Markdown claims ledger is canonical. The registry and generated
`research/claims-index.json` are operational indexes and are checked against
it automatically.

## Reproduction

Python 3.12 or later is required.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m compileall -q src verifier scripts
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

Use `research_health.py --strict` in a clean acceptance worktree. The current
checkout may contain deliberately preserved local untracked evidence; the
non-strict command reports it without treating it as accepted.

Recheck the latest mathematical artifacts independently with:

```bash
.venv/bin/python verifier/verify_phase17.py \
  --artifact-dir artifacts --write-report /tmp/collatz_phase17_verifier.json
```

Acceptance details, finite bounds, commands, test counts, and hashes are in
[the Phase 17 result](PHASE17_RUN_RESULTS.md). Earlier phase and supplement
reports are indexed in [the documentation map](docs/INDEX.md).

## Repository layout

- `src/`: search and generator implementations.
- `verifier/`: logically separate certificate verifiers.
- `tests/`: exact properties, tamper rejection, and adversarial regressions.
- `artifacts/`: generated accepted evidence; do not edit manually.
- `research/`: machine-readable control plane, experiment contracts, and
  scoped audits.
- `docs/`: current status, claim ledger, literature, failures, roadmap, and
  context packs.
- `scratch/`: local untrusted research candidates; never accepted directly.

GitHub pull requests and pushes to `main` run the research-integrity workflow.
A manual workflow runs the complete acceptance suite.

## Evidence warning

`VERIFIED_FINITE` is bounded computation, not an asymptotic theorem.
`CONDITIONAL` retains every named premise. `EXTERNAL_THEOREM` is not internally
reproved. Formal rational, real, or 2-adic trajectories are not automatically
positive ordinary Collatz orbits. A proof or disproof claim must follow the
emergency audit protocol in [AGENTS.md](AGENTS.md).
