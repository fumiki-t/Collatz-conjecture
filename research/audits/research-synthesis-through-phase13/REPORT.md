# Research synthesis audit through Phase 13

**Audit date:** 2026-08-27

**Base `origin/main`:** `6a08972be1069cc00475b3e1bbb7a474527d2037`

**Branch:** `docs/research-synthesis-through-phase13`

**Repository status:** `OPEN`

**`proves_collatz=false`**

## Scope

This was an information-integrity audit, not a new mathematics phase. It read
the canonical control plane, all Phase 1–13 result reports, both supplement
reports, both accepted audit directories, every committed verifier-result
JSON, the source/verifier/test inventory, the local scratch inventory, and the
attached synthesis proposal.

The central output is
[`docs/RESEARCH_SYNTHESIS.md`](../../../docs/RESEARCH_SYNTHESIS.md). Detailed
mathematics stays in the claims ledger, phase reports, and scoped audit reports;
the synthesis links to those sources rather than duplicating their status
authority.

## Sources read

- `AGENTS.md`, `README.md`, `research/README.md`, `research/registry.json`, and
  the experiment schema;
- `docs/CLAIMS_LEDGER.md`, `STATUS.md`, `ROADMAP.md`, `HANDOFF.md`,
  `AI_RESEARCH_GUIDE.md`, `FAILED_APPROACHES.md`, `LITERATURE.md`, and the H54,
  H70, H72 context packs;
- `RESEARCH_HISTORY.md`, `RUN_RESULTS.md`, every `PHASE*_RUN_RESULTS.md`,
  `BRANCH_POINT_RUN_RESULTS.md`, and `TWO_TAIL_RUN_RESULTS.md`;
- `research/audits/garcia-tal-phase12/` and
  `research/audits/renewal-code-pressure/`;
- all committed `artifacts/*verifier*.json` and `*verifier_result.json` files;
- every current scratch filename and the four scratch Markdown audit headers,
  with hashes recorded in [`PROVENANCE.md`](PROVENANCE.md).

The Garcia--Tal, Rozier--Terracol, Fernández--Ibáñez, and Barina metadata or
live primary status pages were rechecked where current publication/computation
state mattered. External proof bodies were not rederived.

## Findings and corrections

### 1. No mathematical status contradiction found

The generated claim index contains 84 unique current claims. Registry active
obligations and watch claims agree with the ledger. All committed verifier
results inspected report acceptance and `proves_collatz=false` where that field
exists. Phase reports and canonical documents consistently retain H54, H70,
H72, C03, C04, C05, the permanent-safe-tail branch, and the nontrivial-cycle
branch as unresolved.

No claim status was changed.

### 2. X02 lacked a direct primary-source pointer

Before this audit, X02's evidence cell referred only to the Phase 7
specification and a local artifact. The statement and
`EXTERNAL_EVIDENCE` status were already appropriately cautious, but a public
reader could not reach the live computation source from the ledger.

The evidence cell now links to the new Barina entry in
`docs/LITERATURE.md`. The live page still stated the completed boundary
`2075*2^60`; work toward the next block was not promoted. This repository still
does not reproduce the distributed computation.

### 3. Public Markdown integrity was not machine checked

`research_health.py` checked navigation freshness, claims, registry, accepted
experiments, verifiers, and artifact hashes, but not missing internal Markdown
targets or leaked local paths. `scripts/check_markdown_links.py` now checks all
tracked Markdown for:

- missing repository-local link targets;
- links escaping the repository;
- absolute macOS home-directory paths and local-only URI schemes outside
  fenced code.

The checker is part of research health, unit tests, and CI. It intentionally
does not validate remote URL availability or Markdown anchor spelling.

### 4. CI's “latest tamper” selection was stale

The workflow still ran `tests/test_phase12_verifier.py` as its latest verifier
tamper suite after Phase 13 acceptance. It now runs
`tests/test_phase13_verifier.py`. Phase 12 remains covered by the manually
dispatched full suite.

### 5. Documentation entry points were duplicated but lacked one synthesis

README, STATUS, HANDOFF, the AI guide, history, and phase reports individually
contained accurate information, but no single document defined all conventions
and connected both major nonperiodic routes to the separate cycle branch.
`docs/RESEARCH_SYNTHESIS.md` now supplies that map. README was shortened to an
entry page, while detailed canonical documents remain authoritative for their
own roles.

The attached proposal suggested an experiment manifest. That was not adopted:
the current experiment schema describes exact mathematical experiments with a
generator, independent verifier, tamper suite, and claim IDs. Inventing those
fields for a documentation audit would weaken rather than improve provenance.
This work is recorded as an audit with its own report and hashes.

### 6. Local Phase 1–2 artifact packaging gap remains

Five large local untracked Phase 1–2 outputs total about 481 MiB. Their hashes
exactly match `RUN_RESULTS.md`, but they are not Git-tracked and are not in the
current global `artifacts/SHA256SUMS`. They were not modified or staged. The
generator/verifier commands remain recorded, so the result is reproducible,
but the five historical outputs are not downloadable from the repository.

This is a provenance/packaging gap, not a new mathematical contradiction.
A later task should choose between compact certificates, release assets, LFS,
or documented regeneration. It must not silently add 481 MiB to Git history.

### 7. Scratch is fully superseded, not accepted

All eight current scratch files predate the accepted Garcia--Tal or Phase 13
audits. They are classified `SUPERSEDED_BY_ACCEPTED_RESULT`; none is copied
into canonical evidence. No post-Phase-13 unverified candidate matching the
suggested terminal-run, height-weighted, fixed-q injectivity, carry-stability,
second-best Christoffel, or Fourier themes was present.

## Files created or updated

Created:

- `docs/RESEARCH_SYNTHESIS.md`;
- `scripts/check_markdown_links.py`;
- this audit's `REPORT.md`, `PROVENANCE.md`, and `SHA256SUMS`.

Updated:

- README, INDEX, STATUS, ROADMAP, HANDOFF, AI guide, failure archive, H54/H70/H72
  context packs, literature, history, claims ledger evidence, registry;
- research health tests/script and the GitHub integrity workflow;
- the generated claims index after the X02 evidence-link update.

## Claim changes

- **Status changes:** none.
- **Statement changes:** none.
- **Evidence metadata change:** X02 now links to the primary computation entry;
  its last-audited date is 2026-08-27.
- **New claim IDs:** none.

## Unresolved obligations

- H54 eventual `M(K_q-1)>H_q` plus finite remainder;
- H70 cross-cylinder dropping-safe spacing;
- H72 positive ordinary-integer exclusion / P80 anti-concentration;
- C03 arbitrary contracting mixed blocks;
- C04 canonical q0 gap residue;
- C05 long-safe pair spacing;
- complete exclusion of nontrivial positive cycles;
- packaging of the five large Phase 1–2 outputs.

## What this audit does not prove

This audit does not prove a new lemma, validate an external proof body, turn a
finite range into an asymptotic result, exclude any counterexample branch, or
prove or disprove the Collatz conjecture.

`proves_collatz=false`.
