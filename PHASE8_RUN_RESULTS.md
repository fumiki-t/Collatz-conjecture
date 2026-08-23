# Phase 8 contracting mixed blocks and octave bridge: run results

Branch: `feat/phase8-mixed-block-octave`

Phase 8 does not prove or disprove the Collatz conjecture. It proves one exact
ordered-block theorem, derives conditional first-octave consequences from the
Phase 7 framework, and performs a bounded falsification search for a stronger
arbitrary-block conjecture.

## Reproduction commands

```bash
.venv/bin/python src/phase8_search.py \
  --artifact-dir artifacts \
  --contracting-max-length 18 \
  --crossing-max-length 22
.venv/bin/python verifier/verify_phase8.py \
  --artifact-dir artifacts \
  --output artifacts/phase8_verifier.json
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
shasum -a 256 artifacts/SHA256SUMS
```

The independent verifier does not import `src/phase8_search.py`. It rebuilds
the affine maps, CRT residues, sign identity, rational logarithm enclosure,
octave exception count, four short-excursion maps, all bounded semigroup rows,
and the mandatory adversarial regressions. Tests require rejection after
tampering with the congruence, sign identity, external exponents, `q0`, `V`,
Denjoy--Koksma variation/error, exception count, a short-map constant, or a
semigroup row.

## C02 — `VERIFIED_THEOREM`

For `A=11101`, `B=1100`, with function order
`F_(r,s)=B^s composed with A^r`, the verifier independently reconstructs

```text
A(x)=(81x+73)/32
B(x)=(9x+5)/16
P=81^r*9^s
Q=32^r*16^s.
```

For an integral realization it derives

```text
u=(49x+73)/32^r
16^s divides u*81^r-108
u*32^r = 73 (mod 49)
v2(u)=2, hence u>=4.
```

Direct coefficient expansion gives the exact sign identity

```text
49*Q*(F_(r,s)(x)-x)
=32^r*(u*(P-Q)+108*(16^s-9^s)).
```

The six exceptional CRT cases are regenerated rather than accepted as input:

| `(r,s)` | least `u` | least source | endpoint | strict core margin |
|---:|---:|---:|---:|---:|
| `(1,2)` | 10,156 | 6,631 | 5,312 | 16,545,536 |
| `(1,3)` | 47,788 | 31,207 | 14,060 | 3,441,471,488 |
| `(1,4)` | 3,058,348 | 1,997,287 | 506,135 | 4,788,482,736,128 |
| `(2,4)` | 1,663,212 | 34,757,735 | 22,295,216 | 40,020,438,614,016 |
| `(3,5)` | 13,460,268 | 9,001,348,199 | 8,221,012,670 | 40,093,814,275,178,496 |
| `(3,6)` | 681,403,180 | 455,677,946,983 | 234,098,318,018 | 182,156,975,520,937,410,560 |

The remaining `r>=4`, `1/2<P/Q<1` regime uses EXT05, Rozier--Terracol
(2026), Lemma B.1. Phase 8 verifies that its exponent is at least 30 and that
the later inequalities are exact. It does not reprove EXT05 and does not use
the paper's finite `13<=q<=18` computation.

Conclusion:

> Every positive integral realization of `A^rB^s`, `r,s>=1`, descends when
> its total multiplier is below one.

This changes C02 from `CONJECTURE` to `VERIFIED_THEOREM` and closes only the
ordered `A^rB^s` family.

## P58 and E13 — conditional octave bridge

Under the least-positive-counterexample and first-crossing assumptions, exact
normalization gives

```text
x_j=2^(theta_j+a_j)*(N+R_j)
R_(j+1)=R_j+(1/3)*2^(-theta_j-a_j)
0<=R_j<=j/3.
```

Thus a defect can disagree with the actual octave index only in a rotation
interval of length
`eta=log2(1+q0/(3V))`. Independent rational logarithm bounds prove
`q0*eta<2`. With the two continued-fraction denominator blocks and EXT04,
the indicator variation contributes total error at most 4, so the integer
exception count is at most 5.

After exact exception damage is deducted from the Phase 7 certificates:

| consequence | lower bound |
|---|---:|
| odd iterates in `[N,2N)` | 31,327,720,457 |
| nonwrapping first-octave pairs at `h=12` | 889,748,819 |
| consecutive contact returns of odd gap at most 2, both endpoints in `[N,2N)` | 7,308,576,455 |

These E13 numbers are `VERIFIED_FINITE` consequences conditional on P58, X02,
EXT04, and the Phase 7 contact certificates. X02 and EXT04 are not reproved.

The four possible short returns are independently reconstructed as

```text
G1(x)=(3x+1)/2
G2(x)=(3x+1)/4
G3(x)=(9x+5)/8
G4(x)=(9x+5)/16.
```

Their exact source intervals and endpoint-parity residue classes are stored in
`artifacts/phase8_short_excursions.json`. No global rank is inferred from this
four-map alphabet.

## C03 — `OPEN`

The secondary search uses the exact partial integer coordinate `U=49x+73`:

```text
A: U=32u     -> U'=81u
B: U=16u+108 -> U'=9u+108.
```

Through block length 18 it reconstructs 79,184 contracting words in total.
The specification's sanity count 79,166 is the subset containing both `A` and
`B`; the difference is exactly the 18 pure words `B^n`. All words are retained
in the artifact. No C03 counterexample was found.

| scope | result |
|---|---:|
| all contracting words, length at most 18 | 79,184 |
| genuinely mixed contracting words | 79,166 |
| all-word minimum descent margin | 1 at `B` |
| mixed-word minimum descent margin | 1,249 at `BBA` |
| first block-boundary crossings, length at most 22 | 12,265 |

The exact nonzero crossing counts are
`1:1, 3:1, 6:2, 8:7, 11:23, 14:99, 16:476, 19:1966, 21:9690`.
Block-boundary safety is not identified with shortcut-step safety. The absence
of a counterexample in this finite range does not promote C03 to a theorem.

The mandatory adversarial audit also reconstructs all 4,096 pairs with
`1<=r,s<=64`: 1,257 are contracting and covered universally by C02, while
2,839 have coefficient-safe noncontracting prefixes and remain adversarial,
not descent conclusions. The closest multiplier above one in this bounded
range is `(r,s)=(31,50)`. The exact `AB` map `(729x+817)/512`, fixed point
`-817/217`, and Phase 7 macro id 0 are preserved as regressions.

## Obstruction / failure report

No new universal hypothesis was refuted, so `docs/FAILED_APPROACHES.md` is not
changed. The surviving obstruction is recorded in
`artifacts/phase8_obstruction_report.md`: C02 does not extend automatically to
arbitrary interleavings, and neither the four-map octave alphabet nor the
`{A,B}` partial integer dynamics currently has a proved common well-founded
potential.

## What this result does not prove

Phase 8 does not prove C03, H54, H57, the existence or nonexistence of a least
counterexample, or the Collatz conjecture. C02 depends on EXT05; the E13
first-octave counts additionally remain conditional on P58, X02, and EXT04.

## Acceptance result and SHA-256

Acceptance result: `161 passed in 132.18s`; the focused Phase 8 suite contains
7 tests, including independent-verifier acceptance and ten tamper-rejection
cases. `artifacts/phase8_verifier.json` records `valid=true`, C02 as
`VERIFIED_THEOREM`, C03 as `OPEN`, and `proves_collatz=false`.

The Phase 8 artifact hashes and complete manifest hash are recorded in
`artifacts/SHA256SUMS` and below after deterministic manifest generation.

```text
45a4373090927bf19390ec423c160fb8511441a9d671ec4e78e2fb441cc40b8d  phase8_ab_semigroup_search.json
9083d09492064ec4f582f20d3b2ccc85f6d59a149bf5627c3b1512c140d6a48d  phase8_c02_theorem.json
05bcf37662fc244009329b8a7f3d4c3b225ef001f9f54599f981dc63b4eccd17  phase8_obstruction_report.md
918390145d9cb267e1b7dd9931670547124a32e86929201b87fba15efc2debd2  phase8_octave_bridge.json
d2e8eeee5ffc1fc6b7b40b3f2da602d9a310375a7b085372ec34e03fe74bd92c  phase8_short_excursions.json
e0c7219a4e1657be25705aa3d9c0384bc0168d7fb3a95dbefb56219289a01933  phase8_verifier.json
```

SHA-256 of `artifacts/SHA256SUMS`:
`e52789a0262ad9b491db47a3a3a59a566b79a4de54d378f970ccaad6813a8aef`.
