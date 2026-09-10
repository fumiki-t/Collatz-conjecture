# Critical-safe-mass supplement — run record

Date: 2026-09-10. Branch: `codex/critical-safe-mass`.
Base main: `df6c063b7428b768b4ea071dd7cea1a5a218220c`.
Latest numbered phase remains 44; `proves_collatz=false`.

## Result and changes to the proposal

P271 establishes the classical safe-word generating-function specialization,
two-sided order `U_n=Theta(2^(rho n)n^(-3/2))` and critical sum <9.
P272 transfers this to permanent-safe positive sources and a nonempty finite
filter whose convergence boundary is exactly rho. P273 sharpens the
renewal-boundary defect lower bound by a log-log term. NG49 retains an
infinite set-theoretic countermodel to mass-only emptiness.

The [mathematical audit](research/audits/critical-safe-mass/REPORT.md) gives
complete quantifiers, proofs and literature boundaries. The current P270
also yields `Y_infinity<=256S_0`, supplying an explicit normalization option
for P273 without relying separately on P221. It is not a strict limit bound.

No fatal mathematical error was found in the proposal. We strengthened its
finite verification by checking every subset sign and disjoint-subset mean
at the tested labeled scales, rejecting float/int scope coercion, adding
translated full filter shells and mandatory families, and rechecking NG45
and both NG46 potentials. The stronger rational coefficient envelopes are
kept explicitly finite, not extrapolated. The general identity is classical;
no literature-wide novelty is claimed.

## Reconstructed finite scope

| Check | Result |
|---|---:|
| Safe/terminal counts, n=0..512 | 513 rows |
| Two-sided rational envelopes, n=1..512 | 512 rows |
| All binary words, lengths 0..18 | 524287 |
| All colors/permutations, labels 1..6 | 50362 |
| Positive cases with inverse hull reconstruction | 6327 |
| Original interval queries, all nonzero | 59 |
| Source occurrences across those queries | 137848 |
| Passing finite-safe occurrences | 5497 |
| Added full filter shells, five offsets | 55 |
| Mandatory family words / finite paths | 48 / 28 |
| Pinned older evidence files | 6 |
| Embedded deliberate corruption rejections | 22 |

Occurrences across queries are not globally distinct sources. The six-label
test is not an infinite proof. Neither the computed interval points nor the
all-one source controls are declared permanently safe. The independent
verifier reports `valid=true`, `generator_imported=false` and no EXT08 input.

## Reproduction

```sh
.venv/bin/python src/critical_safe_mass_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_critical_safe_mass.py --artifact-dir artifacts --output artifacts/critical_safe_mass_verifier.json
.venv/bin/python -m pytest -q tests/test_critical_safe_mass.py tests/test_research_health.py
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/research_health.py --strict
.venv/bin/python scripts/check_markdown_links.py
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

To reproduce without touching accepted files, supply an empty temporary
directory as `--artifact-dir` to both programs and place the verifier output
there. Compare all four new JSON files byte-for-byte. Older evidence is
read from the checkout, not regenerated or modified. Running the verifier
under `python -O` must give identical output and still reject tampering.

The [experiment manifest](research/experiments/critical-safe-mass.json)
records acceptance status, implementation commit and exact test commands.
The global [SHA256SUMS](artifacts/SHA256SUMS) includes all new artifacts.
No artifact or implementation hash is self-referential.

Manifest SHA-256:
`785075e9d48ea40dba851c75287b0b4e6f02a36a12501d99c7982d95bc22bcf7`.
All 301 previous entries are retained, with four new entries:

| Artifact | SHA-256 |
|---|---|
| critical_safe_mass_evidence.json | `01da8c0829d1bf171def08f4a20f995f3cfe7a43a7e56860ce0c0eb5975d3757` |
| critical_safe_mass_regressions.json | `d97f4394e7d5cb00405650f39da7e130be4287f79824cae086f3a63de6f09aa7` |
| critical_safe_mass_scope.json | `f19c5b762826c6f2c085148a49c7fd1dc401c8ba2591ceb571291c2e36a0b4ec` |
| critical_safe_mass_verifier.json | `550e84dccc84780a1bca04bd4a009ac86f6b28e84d91ddbf436762a79bf195be` |

## What this result does not prove

H112/H72/H89/H133 remain OPEN. Critical mass is not emptiness, a supply of
improving ancestors, or P80 address anti-concentration. The log correction
does not bound all values of general orbits/finite trajectories. Renewal
index i is not every odd time q. The infinite filter is not a set of proven
permanent-safe sources. Positive-cycle exclusion remains separate.

## Acceptance record

Accepted against implementation commit
`246c4127c805881fb7cdc88d5891db1c89ccdb94` in a clean detached worktree.
The acceptance metadata is committed separately, avoiding circular hashes.

Clean integrated suite: **493 passed in 267.74s**. Exact command:

```sh
python -m pytest -q tests/test_research_health.py tests/test_phase24_verifier.py tests/test_phase44_properties.py tests/test_phase44_verifier.py tests/test_ext08_scope.py tests/test_transient_sparsity.py tests/test_critical_safe_mass.py tests/test_phase43_properties.py tests/test_phase43_verifier.py tests/test_phase41_properties.py
```

This comprises five control-plane, six Phase 24 verifier, 140 Phase 44,
75 EXT08 scope, 70 transient-sparsity, 65 critical-safe-mass, 98 Phase 43 and
34 Phase 41 property tests. The checkout's existing virtual environment
provided Python; the tested files came from the clean implementation commit.

Initial focused suite: 140 passed in 29.05s, comprising 65 new tests,
70 transient-sparsity tests and five control-plane tests. The embedded 22
corruption checks are reported separately, not added to the pytest count.

All four new JSON files reproduced byte-for-byte in a separate temporary
directory under `python -O`; all embedded tamper rejections remained active.
All 301 older artifact manifest entries are unchanged. Strict research health
passed with no warnings or errors, 364 claims and 305 artifact entries.
The generated claims index, 165 tracked Markdown files' local links,
compileall and diff checks passed. Existing scratch was neither altered nor
staged. The **whole-repository test suite was not run**; historical hash
preservation is not a fresh audit of every older mathematical result.
