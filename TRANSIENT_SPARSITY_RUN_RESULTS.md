# Transient-sparsity supplement — run record

Date: 2026-09-10. Branch: `research/transient-sparsity`.
Base main: `feb29b423d43445f1c7d826d6ef71a25e2854b44`.
Latest numbered phase remains 44. `proves_collatz=false`.

## Result

P269 proves transient recursive capacities; P270 proves `Y_j<256S`
for distinct positive finite input paths, with `13S`/`2S` under input
floors `2^19`/`2^49`. The non-dropping asymptotic is uniform in path length.
P267 already proves the proposed boundary-loss sparsity and is not duplicated.
NG48 retains the repeated-input failure at S=1, first length 39 at that source.

The [mathematical audit](research/audits/transient-sparsity/REPORT.md) gives
quantifiers, all proofs, scope corrections and the independence boundary.
The [experiment manifest](research/experiments/transient-sparsity.json)
records acceptance status, implementation commit, tests and hashes.

The supplied proposal and older Phase 38/43 text conflated actual shell
occupancy with a raw recursive upper-bound array. We corrected the infinite
tail to bound actual occupancies. P229/P260 conclusions/statuses and old
capacity tables/artifacts remain unchanged. No raw-array counterexample is
claimed; the unnecessary inference was not established.

## Independently reconstructed finite evidence

| Component | Scope / result |
|---|---|
| Transient capacity | All 501 rows, N=0..500 |
| Affine words | All 32767 binary words, lengths 0..14 |
| Literal path/windows | 25020 declared cases on starts 1..127 and 703 |
| Terminal deletion | 15420 nonzero cases; maximum 8 on the selected grid |
| Added regressions | 48 family words, 28 normalization paths, source-1 lengths 0..40 |
| Preserved evidence | Three historical files; both NG46 all-length potentials reverified |
| Abstract boundary tests | 26611 subset/M/N cases, including empty and N=0 |
| Verifier | valid=true; generator_imported=false; no floating-point proof decisions |

The four core components exactly match the supplied evidence, whose SHA-256
is `1f5fd8c9f2af21ca6755c4a7ba8c274526af79c0195aad9938ab515984daad38`.
The new accepted files differ in status/schema and add explicit scope and
regression evidence. The supplied code was reviewed and adapted; arithmetic
independence does not imply independent authorship or formal proof checking.

## Reproduction

From a checkout with the development environment installed:

```sh
.venv/bin/python src/transient_sparsity_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_transient_sparsity.py --artifact-dir artifacts --output artifacts/transient_sparsity_verifier.json
.venv/bin/python -m pytest -q tests/test_transient_sparsity.py tests/test_research_health.py tests/test_phase43_properties.py tests/test_phase43_verifier.py
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/research_health.py --strict
.venv/bin/python scripts/check_markdown_links.py
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

For byte reproduction without changing accepted evidence, use `--artifact-dir`
with an empty temporary directory for both programs, and place the verifier's
`--output` in that directory. All four new files must match their committed
counterparts. The verifier reads three immutable older evidence files from
the checkout and imports only the older independent potential checker.

The complete artifact manifest is [SHA256SUMS](artifacts/SHA256SUMS).
Its SHA-256 is
`22b344005071a1f5f58c2a99fd322f64222df2593a8ec66a668731827794695c`.
All 297 pre-existing entries are unchanged; four entries are added:

| Artifact | SHA-256 |
|---|---|
| transient_sparsity_evidence.json | `72089367cc5a903b9b7a843d44663fb3c7e7b7ab630850e96ea611f828652319` |
| transient_sparsity_regressions.json | `f830177804127294c9bb122b94c5b7dc16ac3514873264be15243650031df7e1` |
| transient_sparsity_scope.json | `c911ce2132d0803fa21a3710df19cb7e192eb24182a007928921283aa6995f70` |
| transient_sparsity_verifier.json | `c8bafade646379b4e7e9eccb162365b36307cc59e97481135abf23ea39f9c11c` |

Tests include changed/missing/extra fields, bool/int substitution, historical
hash alteration, raw-capacity tail promotion, repeated-input rejection and
an optimized-Python (`-O`) tamper rejection subprocess.

## What this result does not prove

No Collatz proof, cycle exclusion, H112/H72 resolution, guaranteed improving
ancestor, effective last join, or monotone-defect theorem is supplied.
The all-competitor 256S bound requires distinct target inputs; repeated
targets only have a cycle-deletion witness. Do not use sparsity of actual
occupancies as sparsity of arbitrary upper-bound arrays.

## Acceptance checks

Accepted implementation commit:
`408a6f653a1014f37d7f84173b5cd792b212beee`.
Its clean detached worktree passed **394 tests in 261.98s**, using:

```sh
python -m pytest -q tests/test_research_health.py tests/test_phase24_verifier.py tests/test_phase44_properties.py tests/test_phase44_verifier.py tests/test_ext08_scope.py tests/test_transient_sparsity.py tests/test_phase43_properties.py tests/test_phase43_verifier.py
```

That is five control-plane tests, six Phase 24 verifier tests, 140 Phase 44
tests, 75 EXT08 audit tests, 70 new supplement tests and 98 Phase 43 tests.
Strict research health on the same clean implementation passed with 359
claims, 301 artifact entries, no errors and no warnings. All 163 tracked
Markdown files have valid local links, the generated claim index matches,
and compileall/diff checks pass. All four new artifacts reproduced exactly.
The full repository suite and large older corpora were **not** rerun;
unchanged historical hashes do not constitute a fresh audit of old proofs.

The acceptance metadata is a later commit referring back to this immutable
implementation and its artifact manifest, avoiding self-referential hashes.
Initial focused checks: 168 passed in 7.81s (70 new supplement tests plus
98 Phase 43 tests). This includes 36 changed-field tamper cases, six
missing/extra-field cases, duplicate-key rejection and optimized-Python
rejection. The initial no-op mutation test was corrected to ensure each
tamper actually changes the submitted bytes before testing rejection.
