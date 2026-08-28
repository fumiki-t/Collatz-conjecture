# Phase 15B: ancestral-minimal frontier — run results

Branch: `feat/phase15b-ancestral-frontier`

Base commit: `0fb6eaae467374806720626bbbf9d757c7674db7`

Result commit: `RESULT_COMMIT_PENDING`

Phase 15B proves the least-counterexample ancestral-minimality theorem and
exact cross-Q carry, uniform cylinder dominance, finite renewal decomposition,
Beatty support, shifted-jump, and 3-adic measure lemmas. It independently
audits sources through 5,000,000 and finite word layers through Q=17/19. It
does not prove the eventual H89 barrier or the Collatz conjecture.

The detailed proofs and quantifiers are in
[`research/audits/ancestral-frontier/REPORT.md`](research/audits/ancestral-frontier/REPORT.md).

## Accepted results

- P89 `VERIFIED_THEOREM`: every safe prefix of a least positive
  counterexample is ancestral-minimal.
- P90 `CONDITIONAL`: eventual H89 plus a finite first-crossing remainder
  excludes both finite- and never-crossing least-counterexample cases. The
  latter uses P89 and Phase 6's `H_q>q/6`, a logical step omitted by the
  supplied proposal.
- P91--P95 `VERIFIED_THEOREM`: exact cross-Q/prefix carry, uniform cylinder
  dominance, unique finite renewal decomposition, Beatty support, and shifted
  correction/jump identities.
- P96 `VERIFIED_THEOREM`: the covered 3-adic endpoint union has measure below
  `7/12`; this is not a pointwise ordinary-integer theorem.
- E25 `VERIFIED_FINITE`: `M_star(210)>5000000` by a source-complete scan with
  no endpoint-height cutoff.
- E26 `VERIFIED_FINITE`: exact Q<=17 frontier/trie and Q<=19 same-Q
  compression audits.
- NG27 `REFUTED`: same-Q total compression gain is not universally at most
  three; Q=19 has a gain-four witness.
- H89 remains `OPEN`; `proves_collatz=false`.

The proposal's P86--P88 numbers were not reused because the repository already
assigns those IDs to Phase 15.

## Principal finite results

### Source scan

```text
odd sources scanned:             2,500,000
safe source-endpoint occurrences: 12,443,880
distinct endpoints:              5,297,663
largest endpoint:                659,401,147,466
maximum ancestral-safe depth:    209
M_star(210):                     > 5,000,000
coefficient-crossing termination: 1,114,526
ancestral-domination termination: 1,385,473
```

The record at source 270,271 is cut from coefficient depth 163 to ancestral
depth 160. Source 1,126,015 is cut from 223 to 66. The largest ancestral
record in range is source 1,394,431 at depth 209, then source 1,278,879 reaches
the same endpoint 7,283,621 safely in seven steps.

### Q=17 frontier

| classification | count |
|---|---:|
| coefficient-safe words | 663,535 |
| same-Q uniform dominated | 124,513 |
| ancestor-Q no larger than target-Q, uniform dominated | 320,168 |
| endpoint-specific dominated within Q<=17 | 320,168 |
| shifted-jump dominated | 124,509 |

The agreement of the two 320,168 columns at the top layer is cutoff-specific;
no higher-Q competitors were enumerated for that layer.

### Renewal endpoint trie

```text
Q:    1  2 3 4 5 6 7 8  9 10  11  12 13   14 15    16 17
new:  1  1 0 1 0 2 8 0 28  0 124 602  0 2498  0 12319  0
```

There are 72,804 first-upcrossing blocks through Q=17. The primitive finite
union has exact Haar mass `20113810/43046721`; its conditional unit coverage
is `10056905/14348907` (approximately 0.7008830011). These finite values are
not inputs to P96's analytic bound.

### Q=19 compression obstruction

The Q=19 layer contains 5,936,673 safe words and 4,834,817 endpoint classes.
Among gain-four witnesses the artifact selects the least target source:

```text
d=11111111111111101110000000001, source 44,466,175
a=1111111111101111110100100,     source  2,779,135
common endpoint 96,263,966
d_source+1 = 16*(a_source+1).
```

This refutes only the gain-three bound. It proves no composable or linear
compression theorem.

## Reproduction

```bash
.venv/bin/python src/phase15b_search.py \
  --artifact-dir artifacts --source-bound 5000000 \
  --frontier-max-q 17 --compression-max-q 19
.venv/bin/python verifier/verify_phase15b.py \
  --artifact-dir artifacts --output artifacts/phase15b_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase15b_properties.py tests/test_phase15b_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

The verifier contains none of `phase15b_search`, `from src`, or `import src`.
It scans sources in descending order rather than the generator's ascending
order and reconstructs literal string words rather than packed generator rows.
Tamper tests mutate all six JSON evidence classes and the obstruction report.

Acceptance checks:

```text
generator full bounds:           completed
independent verifier full bounds: valid=true
focused Phase 15B suite:         15 passed in 55.57s
complete repository suite:       247 passed in 343.21s
global artifact manifest SHA-256:
3b250ae2ecd6faee326ba49cdf43aa6f26233029b9d984191e1e76f7b178c2a1
```

## What this result does not prove

- H89 or any eventual lower bound for `M_star`;
- that every safe target has a smaller uniform ancestor;
- P80, H72, or a pointwise consequence from 3-adic Haar measure;
- exclusion of nontrivial cycles;
- the Collatz conjecture.

`proves_collatz=false`.
