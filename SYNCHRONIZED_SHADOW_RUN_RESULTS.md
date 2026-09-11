# Synchronized-shadow-closure supplement — run record

Date: 2026-09-11. Branch: `codex/synchronized-shadow-closure`.
Base main: `12df6b8781957923d8069293f4ad2c0e13c0f7bd`.
Latest numbered phase remains 44; `proves_collatz=false`.

## Outcome

P274--P280/E64 record equal-coefficient coalescence with minimum q=22,
conditional parallel sources and smaller different futures, complete
synchronized peer graphs, proper-subalphabet contractions, and finite affine
self-closure rigidity. NG50 records a complete obstruction to one fixed
three-map integer-compatible affine contraction. No old claim status changes.

The [proof audit](research/audits/synchronized-shadow-closure/REPORT.md)
states all quantifiers and finite-reduction proofs. The
[proposal](research/audits/synchronized-shadow-closure/PROPOSAL.md) is archived
separately. [Backlog B1--B6](research/notes/UNINTEGRATED_THEORY_2026_09_11.md)
remains OPEN, unreviewed material, not accepted theorem evidence.

No fatal mathematical error was found. We strengthened the supplied
verification with negative-state exit ranks, actual mod3-compatible ratio
edges, exact one-position loss margins, all-lift shrink thresholds, mandatory
families and old falsifier checks. We explicitly avoid calling the finite
third peer an infinite ordinary counterexample, or calling disjoint depth
families pairwise coprime. One initial pytest collection error in the adapted
dynamic unittest method was fixed before acceptance.

## Exact finite scope

| Check | Result |
|---|---:|
| All right words, (11,7) and (14,9) | 2332 |
| Same-height states / cases / edges | 223 / 892 / 122 |
| Ratio-2/3 states / cases / edges | 674 / 2696 / 334 |
| Same-height / ratio live states | 15 / 13 |
| Added mod3-compatible literal ratio edges | 334 |
| q<=20 width comparisons / q=21 complete cases | 20 / 24 |
| Affine scale/correction grid | 574574 |
| Complete symbolic contractions, all integer-incompatible | 1179 |
| Four-block schedules / lifted pairs | 1364 / 4092 |
| Pair and third-source literal steps | 570663 |
| Even third-source finite checks | 1023 |
| Proper-subalphabet lifted pairs | 1134 |
| Repeat lifts (r=0..16, four lifts each) | 68 |
| Mandatory family words / finite paths | 48 / 28 |
| Pinned prior evidence files | 6 |

Schedules, lifted pairs, sources and literal steps are different counting
domains. No earlier chat counts are added. All seven core mathematical
components match the supplied evidence exactly; accepted schema/status and
additional scope/regression evidence are separate audited changes.

## Reproduction

```sh
.venv/bin/python src/synchronized_shadow_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_synchronized_shadow.py --artifact-dir artifacts --output artifacts/synchronized_shadow_verifier.json
.venv/bin/python -m pytest -q tests/test_synchronized_shadow.py tests/test_research_health.py
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/research_health.py --strict
.venv/bin/python scripts/check_markdown_links.py
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

For nondestructive reproduction, pass an empty temporary directory to both
programs and put the verifier output there. Compare all four new JSON files
byte-for-byte; the verifier also runs under `python -O`. It reads pinned
historical evidence from the checkout without rewriting it. The generator
and verifier use different graph, decoding and correction reconstructions;
this is not independent authorship or machine-formalized infinite proof.

The [experiment manifest](research/experiments/synchronized-shadow-closure.json)
records acceptance status, implementation commit and exact test command.
The [SHA-256 manifest](artifacts/SHA256SUMS) covers generated evidence.
Manifest SHA-256:
`d49deca6bc2ad18cda7499a8c96c4daedb04bad00b8e1f36f770e6329f6f0bca`.
All 305 prior entries are unchanged; four entries are added:

| Artifact | SHA-256 |
|---|---|
| synchronized_shadow_evidence.json | `e6b74fd9cfd4493c30190418d096078cb8f0475c4f7e9917a283a3dab1ad14f6` |
| synchronized_shadow_regressions.json | `c0e1f32591a2c26c24bc8ec27e4d02c943e4750f86cf2f893506468ce07ef5b8` |
| synchronized_shadow_scope.json | `01df028d54df078c9036653c181641e8c893f947653cfa782fd3eb07f3666b06` |
| synchronized_shadow_verifier.json | `4c558544b24389f21301d384247edd1613f61971a74fcc05d6436592fb00541e` |

Acceptance references the implementation commit below; metadata is recorded
in a separate commit to avoid circular hashes.

## Acceptance record

Accepted against implementation commit
`f63291994276caf25d8c74c216ba76c51f093933` in a clean detached worktree.
**444 passed in 51.20s**, with this exact command:

```sh
python -m pytest -q tests/test_synchronized_shadow.py tests/test_phase41_properties.py tests/test_phase42_properties.py tests/test_phase43_properties.py tests/test_phase43_verifier.py tests/test_critical_safe_mass.py tests/test_transient_sparsity.py tests/test_research_health.py tests/test_ext08_scope.py
```

This comprises 65 new tests, 34 Phase 41 properties, 32 Phase 42 properties,
98 Phase 43, 65 critical-safe-mass, 70 transient-sparsity, five control-plane
and 75 EXT08 scope tests. The existing repository virtual environment
provided Python, while tested files came from the clean implementation commit.

Initial focused suite: 65 passed in 8.85s, including the supplied 28
corruption-rejection tests plus new scope, integrality, graph and arithmetic
checks. This count is not a claim that the full repository suite was run.
An initial dependency suite passed 364 tests in 25.92s: this supplement,
Phase 41/42 property tests, Phase 43 properties/verifier, critical safe mass
and transient sparsity. An optimized
`python -O -m unittest discover -s tests -p test_synchronized_shadow.py -q`
run passed all 32 unittest cases in
1.230s, including all 28 supplied corruption tests.

All four new artifacts reproduced byte-for-byte in a separate directory,
including the verifier report under `python -O`. Strict research health was
valid with no warnings/errors, 373 claims and 309 artifact entries. All
169 tracked Markdown files' local links, generated claims index, compileall
and diff checks passed. Existing scratch was not altered or staged; all
305 older artifact manifest entries are unchanged. Prior main's CI run
34479635402 was independently confirmed completed successfully.

The **whole-repository suite was not run**. Old hashes do not constitute a
fresh audit of every historical mathematical result; large historical
enumerations were not rerun merely for this supplement.

## What this result does not prove

No infinite positive ordinary left source is constructed or generally
excluded. No coverage of all ancestors, all same-height sources, or the full
safe language is proved. Different-future contraction need not preserve a
shared-future class or close the image language. Fixed affine impossibility
does not prohibit general stateful rewriting. Arbitrary-depth lifts spend
a source-dependent finite valuation resource. Backlog B1--B6 is not accepted.
H112/H72/H89/H133 remain OPEN; positive cycles remain separate; EXT08 is unused.
