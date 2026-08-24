# Phase 9 two-sided criticality and near-diagonal residues: run results

Branch: `feat/phase9-two-sided-criticality`

Base commit: `ad4f8848efa3aafc211cf80089563ae9406bc418`

Phase 9 does not prove or disprove the Collatz conjecture. It sharpens the
conditional Phase 7/8 first-crossing scenario, refutes a contact-only proof
mechanism, and independently verifies several exact finite and symbolic
consequences. The simultaneous residue exclusion C04 remains `OPEN`.

## Reproduction commands

```bash
.venv/bin/python src/phase9_search.py \
  --artifact-dir artifacts \
  --small-layer-max-q 21 \
  --reverse-max-a 30 \
  --paradoxical-max-length 21
.venv/bin/python verifier/verify_phase9.py \
  --artifact-dir artifacts \
  --output artifacts/phase9_verifier.json
.venv/bin/python -m pytest tests/test_phase9_properties.py \
  tests/test_phase9_verifier.py -q
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
shasum -a 256 artifacts/SHA256SUMS
```

The independent verifier does not import `src/phase9_search.py`. It rebuilds
the forced-contact truth table, every reduced contact-dual candidate with
denominator at most 256, the short-gap count, endpoint identities and
congruences, the continued-fraction barrier, all configured reverse coefficient
pairs and mechanical residues, all 22,475,497 small-layer words, and every
parity word through shortcut length 21. The tests also require rejection of
tampered closure, dual integral/variation, gap, displacement, congruence, G4,
continued-fraction, reverse-residue, and two-sided-residue fields.

## P59 — `CONDITIONAL`

The exact defect recurrence is

```text
a_(j+1)=a_j+b_j-e_j.
```

If `a_j=0` and the rotation phase gives `b_j=1`, positivity forces `e_j=1`,
and therefore `a_(j+1)=0`. The successor phase lies in H and its contact weight
is exactly `2/3` of the original contact weight. The recurrence and closure are
symbolically verified. P59 remains `CONDITIONAL` because its research use is
inside the least-positive-counterexample and first-crossing framework.

## NG17 — `REFUTED`

Forced closure plus weighted contact pressure alone cannot exclude every
finite critical word. For a zero-indexed parity word the construction must
start with `c_0=1`; this corrects the unrestricted-indicator wording in the
specification. After that correction, the all-contact choice

```text
c_j=1, a_j=0, d_j=floor(j*log_3(2)), e_j=b_j
```

obeys closure and strictly satisfies the required weighted pressure at q0.
It does not impose the endpoint or least-positive inverse-parity residue.
Thus NG17 refutes only the contact-only strategy; stronger simultaneous
2-adic/3-adic or endpoint mechanisms survive.

## Exact contact dual and E14

For the specified piecewise contact dual, exact rational-logarithm intervals
and all reduced fractions of denominator at most 256 select

```text
lambda = 143/199
closure-aware contact lower bound = 35,251,435,772
Phase 7 contact lower bound       = 31,327,720,462
strict improvement                =  3,923,715,310
```

The selection is optimal only on that explicit finite rational grid; no global
continuous optimum is claimed. The verifier reconstructs the integral,
circle total variation `623/1194`, two-block Denjoy--Koksma error `623/597`,
and endpoint damage `56/199` using exact intervals. EXT04 itself is not
reproved.

The exact short-gap identity is

```text
(M-1)-floor((q0-M)/2).
```

After deducting at most ten damaged edges from the five Phase 8 octave
exceptions, E14 gives:

| contact input | first-octave short-return lower bound |
|---|---:|
| Phase 7 baseline | 10,962,864,687 |
| closure-aware Phase 9 bound | 16,848,437,652 |

E14 is `VERIFIED_FINITE` with the explicit conditional/external dependencies
P58, P59/P57, X02, EXT04, and the Phase 7 contact certificate.

## P60 and P61 — endpoint displacement and minimality

The independent verifier reconstructs

```text
S(a)=3*N*delta+3*(1+delta)*d
d=(S(a)/3-N*delta)/(1+delta)
0 <= d <= 4,142,380,786 < 2^32.
```

It also checks `N,X<2^72` and the exact scalar inequalities needed for the
minimality witnesses. Under the same least-counterexample first-crossing
assumptions, the endpoint satisfies

```text
N odd, X odd, d even,
X = 3 (mod 4), X = 1 (mod 3),
X = 1 or 7 (mod 9), hence X = 7 or 19 (mod 36).
```

For `G4(x)=(9x+5)/16`, its endpoint `y` is odd and `2 mod 3`; the exact
predecessor `z=(2y-1)/3` is positive, odd, maps to `y`, and is smaller than N
in the first-octave scenario. This conditionally forbids G4. P60 and P61 are
`CONDITIONAL`, not unconditional orbit theorems.

## P62 — reverse continued-fraction barrier

The uniform reverse coefficient threshold is

```text
2^L/3^a >= V/(V+dmax).
```

Exact logarithm intervals and a unimodular continued-fraction certificate give

| role | `(a,L)` |
|---|---:|
| previous insufficient semiconvergent | `(478054749257,757698850864)` |
| first coefficient pair not excluded | `(615582794569,975675645481)` |

The certificate uses lower base `(103768467013,65470613321)`, upper parent
`(217976794617,137528045312)`, next partial quotient 5, and determinant -1.
P62 is `CONDITIONAL` and coefficient-only: it does not construct a valid
reverse Collatz path.

The finite reverse audit covers all 287 contracting coefficient pairs through
`a<=30` and 30 explicit lower-mechanical exponent words. All mechanical rows
violate least-counterexample minimality in the q0 near-return scenario. This
does not enumerate every composition of L into a positive exponents; that
combinatorial gap is recorded as an obstruction rather than a zero-survivor
theorem for arbitrary reverse words.

## C04 — `OPEN`

For each first-crossing word the generator and verifier independently rebuild

```text
r2 = -B*3^(-q) mod 2^K
r3 =  B*2^(-K) mod 3^q
3^q*r2+B = 2^K*r3.
```

All coefficient-safe first-crossing words through `q=21` were enumerated:

```text
q= 1.. 8: 1, 1, 2, 3, 7, 12, 30, 85
q= 9..14: 173, 476, 961, 2,652, 8,045, 17,637
q=15..18: 51,033, 108,950, 312,455, 663,535
q=19..21: 1,900,470, 5,936,673, 13,472,296
total:     22,475,497
```

There are no nontrivial paradoxical canonical first-crossing words in this
finite range and no row in the q0 near-diagonal box, but q0 itself was not
enumerated. Every full row is folded, in a specified binary encoding and
order, into a per-layer SHA-256 digest; the verifier independently reproduces
all digests. C04 remains `OPEN` because no asymptotic two-sided residue
exclusion or lossless scalable meet-in-the-middle certificate was obtained.

This is an explicit storage-format deviation from the request to retain every
row as an individual record. Materializing 22,475,497 verbose JSON rows would
create a disposable multi-gigabyte artifact, so the committed certificate
stores layer summaries, extrema, every paradoxical or congruence-plus-octave
candidate, and an ordered digest covering every row. Independent full
re-enumeration verifies the omitted rows; they are not inferred from the
digest alone.

## Direct paradoxical tree

Every parity word through shortcut length 21 was reconstructed. Exactly five
positive nontrivial paradoxical cylinders occur, all at length 8:

| word | source | endpoint |
|---|---:|---:|
| `01011101` | 18 | 20 |
| `10110011` | 25 | 26 |
| `10111010` | 9 | 10 |
| `11001101` | 19 | 20 |
| `11101001` | 7 | 8 |

No additional cylinder occurs through length 21. This bounded tree produces
neither a new global rank nor a counterexample to C04. Rozier--Terracol's
Theorem 1.3 and Winkler's larger recursive stopping-time trees are external
results and are not reproved by this finite audit.

## Mandatory adversarial audit

The production run includes exact regressions for `2^m-1` through `m=64`,
`8^m-5` through `m=32`, all 4,096 twelve-block words in `(110|111)^*`, A, B,
1,024 pairs `A^rB^s` with `1<=r,s<=32`, Phase 7 macro id 0, and Phase 8 BBA.
Passing these finite regressions is not evidence of universality.

## What this result does not prove

Phase 9 does not prove C04, C03, H54, H57, the existence or nonexistence of a
least counterexample, or the Collatz conjecture. It does not reprove X02,
Denjoy--Koksma, Rozier--Terracol Theorem 1.3, or Winkler's external tree
results. The q<=21 and length<=21 searches cannot establish eventual behavior.

## Acceptance result and SHA-256

Acceptance result: `170 passed in 191.88s`. The focused Phase 9 suite passes 9
tests, including independent-verifier acceptance and tamper rejection.
`artifacts/phase9_verifier.json` records `valid=true`, C04 as `OPEN`, and
`proves_collatz=false`.

```text
baddc05f70fb4e99e686989d19c9bef70d7f619a41a20102e51d2a27c19972f7  phase9_contact_dual.json
73f65a53de2744b80bc2e8476e11b2cd594c432e2d16c338a421a1e5a5c9b04c  phase9_endpoint_displacement.json
6f44613ad96f81b7ec2345a934ab21a739515f1efc663afd5d611c8abd432dbb  phase9_forced_contact.json
c2f1b70e344ab90b00d2e0454bd34c5201b2c4c576b220f834e79d2a355fd520  phase9_obstruction_report.md
5296e026b219f4e750490d3837cb3cf2390aabeca9cccca6fff4aa5a8ecc0493  phase9_paradoxical_tree.json
8e12709c598325d102a9ddd8549436c63b54442f0e5442fe2d91f5b9de6d0090  phase9_reverse_barrier.json
535ef413e9241ac0b93f9c53314f3cb08f677a2d85f49a337074d85565fc9d18  phase9_reverse_residues.json
c403d3a01604d12df34781d344672c2b00297710c1b7403a8e156307cb4fab44  phase9_short_return_bound.json
a62dd80bfc96d42f40f0458c075c384a4f7346b7c8ed06945360aae55a445e12  phase9_two_sided_residues.json
9056b183f9f9863fcd050e5486fc84b155cb3532727ba34809636c855934d8c9  phase9_verifier.json
```

SHA-256 of `artifacts/SHA256SUMS`:
`922ca9d95d2b35efd7bb030b0df7b4ece77486cf2f58fa323cbeafdf65430918`.
