# Collatz conjecture research archive

> 2026-09-10 [EXT08 scope audit](EXT08_SCOPE_AUDIT_RESULTS.md): EXT08 is now `OPEN`,
> not an accepted external premise and not a refuted theorem statement.
> P119/P121/P123/P124/P128 retain their conditional historical routes;
> P127, internal permanent-safe reduction and Phases 42--44 remain intact.
> Older artifact status snapshots are historical, not current claim authority.


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

The [synchronized-shadow audit](SYNCHRONIZED_SHADOW_RUN_RESULTS.md) classifies
parallel sources under exact block synchronization and certifies an integer
obstruction to one fixed affine contraction of three specified maps. It does
not classify all ancestors or construct an infinite positive source. Earlier
unreviewed theory is preserved separately, not as accepted evidence.

The [critical-safe-mass supplement](CRITICAL_SAFE_MASS_RUN_RESULTS.md) proves
sharp safe-word counting and a translated critical-mass bound. The associated
finite-prefix filter is infinite: summability does not solve Collatz or
prove that a permanent-safe source exists.

The [transient-sparsity supplement](TRANSIENT_SPARSITY_RUN_RESULTS.md) adds
uniform normalization bounds for distinct positive finite paths, with no
assumption about their infinite future. It also corrects the distinction
between actual occupancy and recursive upper-bound tables. No improving
ancestor or Collatz proof follows.

Phase 44 is the latest numbered research layer. Counting mechanical factors with zero
insertions/deletions strengthens the necessary downward-variation budget
without assuming monotone defect. It excludes one oscillating formal model
as a positive ordinary source, with a nonvacuous million-step independent
audit and eight finite repeat-and-split certificates. It does not force a
dominating ancestor or resolve H112. See the [Phase 44 results](PHASE44_RUN_RESULTS.md).

Phase 43's finite rational potentials
now certify coefficient maximality against every positive ancestor, over
all lengths and odd counts. The independent audit covers 2,668 queries.
A minimal finite counterexample, `7 -> 11 -> 17 -> 26 -> 13`, shows that
even this maximality does not force monotone defect. Search budgets still
return `UNKNOWN`; neither universal termination nor H112 is proved.
See the [Phase 43 results](PHASE43_RUN_RESULTS.md).

Phase 42's mechanical-factor capacity proves a
square-root lower bound for nondecreasing defects and excludes a positive
ordinary source for the specific square-root formal model of Phases 13/41.
This does not exclude general safe words or prove H112. Independent finite
certificates also establish the minimum odd count 22 for negative same-q
carry. See the [Phase 42 results](PHASE42_RUN_RESULTS.md), including the
explicit limits of its finite capacity sample.

The Phase 40 normalized-height reduction survives and is simplified in
Phase 41. Minimizing a finite normalized
height gives a permanent-safe representative whose every prefix is globally
shortest among positive paths with the same odd count. This proves that the
open source-lift statement H112 would exclude the entire nonperiodic branch
without external evidence X02. It does not prove H112. Bellman redundancy
stabilizes, but no effective stopping rule is supplied. An exact length-25
counterexample shows why shifted-correction rewrites still need safety tests
and strict-valley rescue. Alternate-predecessor clouds supply additional
collision-free sets; their weighted valuation bound is already a direct
consequence of orbit sparsity. Arbitrary-area positive cycles remain separate.
H72, H133, and the broader H54, H70, H89, H104, H105, H112, H141, H172, C03,
C04, and C05 obligations remain open.

Start with the [research synthesis](docs/RESEARCH_SYNTHESIS.md). It defines the
map and conventions, summarizes Phases 1–43, separates internal and external
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
.venv/bin/python verifier/verify_phase44.py --artifact-dir artifacts
```

Acceptance details, finite bounds, commands, test counts, and hashes are in
[the Phase 44 result](PHASE44_RUN_RESULTS.md). Earlier phase and supplement
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
