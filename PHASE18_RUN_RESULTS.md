# Phase 18: affine finite-state trichotomy — run results

Branch: `feat/phase18-affine-trichotomy`

Base commit: `b20bb167631a15e518c0460a64dbe42ed5116295`

Result commit: recorded by the accepted experiment manifest

Phase 18 treats the supplied note as an untrusted proposal.  It proves a
finite affine-graph trichotomy after repairing the proposed one-switch normal
form and the mixed-SCC threshold.  It does not show that the full H72 language
has a closed finite graph, and the Collatz conjecture remains open.

The detailed proof and quantifiers are in
[`research/audits/affine-trichotomy/REPORT.md`](research/audits/affine-trichotomy/REPORT.md).

## Accepted results

- P107 `VERIFIED_THEOREM`: if a finite affine graph has no mixed SCC, every
  coefficient-safe finite path has uniformly bounded normalized correction.
- P108 `VERIFIED_THEOREM`: with no mixed SCC, bounded-final-discrepancy safe
  paths have bounded length unless a positive SCC reaches a negative SCC; the
  reachability also constructs arbitrarily long such paths.
- P109 `VERIFIED_THEOREM`: a mixed SCC has a formal infinite safe path with
  bounded multiplier and normalized correction growing linearly.
- P110 `CONDITIONAL`: assuming EXT07, the particular balanced P109 itinerary
  cannot have a positive ordinary source.
- P111 `VERIFIED_THEOREM`: canonical 2-adic source residues lift by
  `lambda*2^L`, and a fixed positive source forces all sufficiently late lifts
  to be zero.
- E30 `VERIFIED_FINITE`: 4,181 small graphs, a 512-packet mixed schedule,
  current-model applicability, and 74 adversarial rows are independently
  reconstructed.
- NG30 `REFUTED`: the sign-pure SCC normal form need not have one global
  positive-to-negative switch.
- H72 remains `OPEN`; `proves_collatz=false`.

## Proposal corrections

The correct sign-pure normal form follows the finite SCC condensation and may
have a graph-bounded number of sign changes.  A four-stage `+,-,+,-` chain
gives an exact infinite counterfamily to the stronger single-mountain claim.

For a negative packet `B`, let `m_B` be its least internal prefix
coefficient.  The switching construction uses the stronger exact condition
`H>1/(m_B*c_B)` so every internal prefix remains safe.

## Exact finite data

```text
deterministic partial graphs, vertices 1..3:  4181
Type I / Type II / Type III:                  1696 / 176 / 2309
safe-path audit depth:                        12
terminal multiplier cap:                      4
mixed one-state schedule:                     512 packets, H=8
mandatory/adversarial rows:                    74
normal-form counterfamily parameters:          2,3,4,8,16,32
```

Every classification and path decision uses integers or exact rational
arithmetic.  Floating point does not decide acceptance.

## Existing-model conclusion

Phase 7 and Phase 8 give mixed coefficient alphabets only as
overapproximations.  Phase 10/11/13 require growing state, Phase 14 is not
prefix-closed, Phase 16 is a local sieve, and Phase 17 is an expanding Type I
sublanguage.  No accepted artifact currently gives a prefix-complete closed
finite graph for the full H72 branch.

## Reproduction

```bash
.venv/bin/python src/phase18_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase18.py \
  --artifact-dir artifacts --write-report artifacts/phase18_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase18_properties.py tests/test_phase18_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

The verifier contains none of `phase18_search`, `from src`, or `import src`.
It uses an explicit affine sum, mutual-reachability SCCs, reverse graph
enumeration, literal schedule reconstruction, and current project-file
digests.  Tamper tests alter each evidence class and require rejection.

The result commit, test counts, timings, and manifest hash are fixed in
`research/experiments/phase18-affine-trichotomy.json` after acceptance.

## What this result does not prove

- a finite-state presentation of every H72 candidate;
- positive ordinary integrality of a formal 2-adic source;
- exclusion of every mixed-SCC itinerary;
- H72, H89, H104, H105, nontrivial-cycle exclusion, or Collatz.

`proves_collatz=false`.
