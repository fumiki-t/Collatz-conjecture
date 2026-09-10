# Phase 44 run results — zero-edit capacity

Date: 2026-09-10. Branch: `feat/phase44-edit-capacity`.
Base: `44430b21705bd69acb6cc29760ee27bdf2433b1f`.
`proves_collatz=false`; H112/H72/H89/H133 remain OPEN.

## Outcome

P262--P264 prove zero-edit capacity and stronger necessary downward-variation
costs without defect monotonicity. In particular D=o(q) forces
H/log_2(q)->infinity on a positive permanent-safe orbit. P265/P266 exclude
one oscillating formal model's positive ordinary source, despite vacuous
pure CAP at every depth and no same-vertex gain after its specified prefix.
P267 separately extends sparsity to finite distinct trajectory segments
with a terminal loss. No new external theorem is required.

The proposal and accepted proofs are separated in the
[audit](research/audits/edit-capacity/REPORT.md) and
[proposal](research/audits/edit-capacity/PROPOSAL.md). Its older Phase 42 base
did not overwrite Phase 43. Both NG46 certificates, at (7,4) and (703,80),
are rechecked. The existing untracked scratch directory is preserved and
excluded from publication.

## Independently reconstructed finite results

| Quantity | Exact result |
|---|---:|
| Formal odd steps / shortcut bits | 1,000,000 / 1,584,925 |
| Maximum defect H / downward variation D | 38 / 22,149 |
| Low-edit window occurrences / distinct words | 590,784 / 966 |
| r=1 EDIT-CAP violation margin in the formal model | 269,665 |
| Repeat-and-split certificates | 8, source bounds 2^8 through 2^1024 |
| Largest required repeat prefix | 25,756 bits (not claimed minimal) |
| Ordinary odd sources / valid prefix queries | 256 / 5,090 |
| Queries with windows / safe queries | 3,888 / 735 |
| Exact ordinary inequalities | 20,360 |
| Small edit balls / alignment words | 24 / 1,364 |
| Alignment widths / low-edit memberships | 10,691 / 59,372 |

The new ordinary audit includes unsafe prefixes and one traversal of the
trivial cycle (distinct inputs, repeated closing endpoint). It stops on
intermediate even-state repetition too. The generator replays 61 inherited
family words and 22 named controls; all 61 family sources plus 24 additional
Mersenne/8-power family sources also receive the new capacity audit.

The checker imports no corresponding generator. It uses epoch/event jumps,
a different exact logarithm enclosure, range-add charges, byte-word sets,
inverse zero-edit DP, and full-state orbit iteration. Repeat certificates
also have their actual affine heights checked at both repeated starts.
Acceptance uses explicit exceptions and rejects tampering under `python -O`.

## Reproduction

From the repository root:

```bash
.venv/bin/python src/phase44_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase44.py --artifact-dir artifacts --output artifacts/phase44_verifier.json
.venv/bin/python -m pytest -q tests/test_phase44_properties.py tests/test_phase44_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q tests/test_phase37_properties.py tests/test_phase42_properties.py tests/test_phase42_verifier.py tests/test_phase43_properties.py tests/test_phase43_verifier.py
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

Strict health is run from a clean detached implementation-commit worktree;
the user's scratch files are not removed to manufacture a clean main.
The test suite also regenerates all four generator outputs in a separate
temporary directory and independently verifies them byte-for-byte.

Artifacts: `phase44_model.json`, `phase44_finite.json`,
`phase44_regressions.json`, `phase44_theory.json`, `phase44_verifier.json`
under [artifacts](artifacts/SHA256SUMS). New code is
[generator](src/phase44_search.py) and [verifier](verifier/verify_phase44.py).
The [experiment contract](research/experiments/phase44-edit-capacity.json)
was created before acceptance-bound computation.

## Acceptance record

Initial focused run: **133 passed in 25.53s**. After adding finite-summary
and regression mutation cases, the integrated run passed **145 tests in
78.02s**: 140 Phase 44 tests and five control-plane tests. The five selected
dependency files passed **201 tests in 47.12s** (Phase 37 properties, Phase 42
properties/verifier, Phase 43 properties/verifier). Thus 346 distinct scoped
tests have passed before the clean CI-equivalent run. The whole repository
suite has not been rerun.

Independent verifier: `valid=true`, `generator_imported=false`,
`proves_collatz=false`. The regeneration test reproduces all four generator
outputs byte-for-byte in a separate temporary directory and verifies them.
All 159 tracked Markdown files pass the link checker; the generated claims
index has 352 entries and registry health reports no errors or warnings.

The [SHA-256 manifest](artifacts/SHA256SUMS) contains 293 entries, with the
previous 288 retained unchanged. Its own SHA-256 is
`23d0216cbda7b233ae9725cbb4f93b68459fecfad62f6790ac8a6b963539018c`.
Clean-worktree acceptance of the implementation commit is recorded below
after that final pass; this paragraph does not claim the whole suite ran.

## What this result does not prove

The model's finite excess requires the distinct-state premise; only its
separate matching-then-splitting certificates avoid global distinctness.
Finite statistics do not prove any asymptotic theorem. The specified
model's all-source exclusion follows from P266's written proof, not eight
source bounds. Its 2-adic source still exists, and all-Q geodesicity is not
established. Neither many zero edits nor height growth forces a positive
dominating ancestor without a new source/carry/lift theorem. The positive
cycle branch remains separate. Collatz is not proved or disproved.
