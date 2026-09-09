# Phase 41 — shifted decoding, all-Q ancestors, and a formal no-gain model

Base: `4a814b3b376d491e602310e41cbf30725f9fd5b6` (Phase 40 acceptance).
Branch: `feat/phase41-shifted-decoder-all-q`.
The supplied September 9 bundle was treated as an unaudited proposal.
See the [`complete audit`](research/audits/shifted-decoder-all-q/REPORT.md)
for exact proofs, quantifiers, input hashes, and limitations.

## Adopted results and boundaries

- P242/P243 receive an all-positive-source normalized-height reproof and the
  converse: H112 is equivalent to exclusion of positive nonperiodic orbits,
  without X02. This reorganizes the existing reduction; it does not prove H112.
- P247 extends eventual maximum-ratio stabilization to all Q and lengths.
  It still supplies no effective last-coalescence index.
- P248 gives the complete shifted decoder, including invalid triples and
  empty/all-zero/all-one boundaries. P249 allows mixed 2/3 source rewrites,
  even competitors at h=R, and unsafe competitors for least ordinary sources.
- P250 supplies the exact safe gain cap and finite weight cutoff. NG44
  preserves the least hole at `(ell,J)=(14,24573)`, weights `{1,2,5,6}`.
- P251 proves `C_u<=8` and the all-depth bound `J/3^t<=1753/729<3`
  for `w=110111111u`. NG45 consequently refutes forcing a same-vertex
  improvement from the stated formal analytic conditions alone.

The formal word has a coherent 2-adic source, but no verified positive
ordinary source or full same-Q/all-Q geodesicity. It is not an H112 or
Collatz counterexample. The source-7 no-rewrite control is convergent.
Mixed ternary factors alone do not add a minimal-source obstruction when
`3|(S+1)`, since the elementary predecessor `(2S-1)/3` already dominates.

## Independently verified finite scope

| Component | Result |
|---|---|
| Complete decoder | 32,767 words, L=0..14; 255 valid and 10,291 rejected boundary triples |
| Complete tail fibers | All ell<=14; no holes through 13, two hole vertices at 14 |
| Mixed rewrites | 4,192 rows, ell<=8/R<=6/v3<=2; 658 even competitors; 645 safe-target gain checks |
| Formal model | 512 odd steps of u, 798 full bits, ten nested source checkpoints |
| Broad ancestor oracle | 125 target instances; all dominating positive sources and L'=0..10, all q'; 718 hits |
| Preserved controls | Six mandatory families, NG22/24/25/26/28/43, source167, source7, longer cross-Q and even competitors |

The supplied length-27 C++ computation was not rerun or accepted. Finite
observations of no unsafe alternative do not supersede NG43. The bounded
ancestor no-hit result is explicitly **not** an all-Q geodesic certificate.

## Independence and reproduction

The generator uses leading-bit shifted decoding and CRT construction. The
verifier imports no generator: it reconstructs the complete finite image
using positional sums, ordinary source lifts, and actual forward iteration.
All decisions use arbitrary-precision integers or exact rationals. Tamper
tests cover arithmetic, scope, completeness digests, statuses and proof flags.

From the repository root:

```sh
.venv/bin/python src/phase41_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase41.py --artifact-dir artifacts --output artifacts/phase41_verifier.json
.venv/bin/python -m pytest -q tests/test_phase41_properties.py tests/test_phase41_verifier.py tests/test_research_health.py
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
```

A bounded ad-hoc ancestor query (all Q, including longer competitors):

```sh
.venv/bin/python src/phase41_search.py --endpoint 31 --target-word '' --maximum-length 10
```

The length cap is mandatory. Returned `hits` rows are `[source,L,q,word]`;
`all_Q_geodesic_certificate` stays false even if the list is empty.

For an isolated byte-for-byte reproduction, set `--artifact-dir` to a fresh
temporary directory in both commands and compare the six `phase41_*.json`
files. Verify the repository-wide SHA-256 manifest from `artifacts/` with
`shasum -a 256 -c SHA256SUMS`. Strict health acceptance is performed in a
clean detached worktree; the pre-existing untracked scratch directory is
preserved outside the published commit.

Final test timings, clean-worktree results, immutable implementation commit,
and manifest SHA-256 are recorded in the
[`experiment contract`](research/experiments/phase41-shifted-decoder-all-q.json).
Only the reported scoped tests are asserted; a whole-repository suite is not
implied by successful focused tests.

## What this result does not prove

H112/H72/H89/H133 remain `OPEN`, and `proves_collatz=false`. The missing
result is an ordinary-source ancestor-existence or nonzero-lift theorem that
survives NG45, source167, signed carry and unsafe/even/longer competitors.
Complete decoding and non-effective stabilization do not provide it. The
positive-cycle branch remains separate.
