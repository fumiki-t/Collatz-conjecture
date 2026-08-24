# Phase 10 gap renewal: run results

Branch: `feat/phase10-gap-renewal`

Base commit: `d1017982290e71b92438d07c6949f282e5bd1d96`

Phase 10 does not prove or disprove the Collatz conjecture. It exactly reduces
the Phase 9 C04 box to one gap residue, proves a conditional renewal barrier,
proves a formal rational-cycle lemma, and independently reconstructs a finite
safe-pair spacing experiment. C04 and the new spacing target C05 remain
`OPEN`; `proves_collatz=false`.

## Reproduction commands

```bash
.venv/bin/python src/phase10_search.py \
  --artifact-dir artifacts \
  --spacing-bound 1500000 \
  --layer-max-q 15
.venv/bin/python verifier/verify_phase10.py \
  --artifact-dir artifacts \
  --output artifacts/phase10_verifier.json
.venv/bin/python -m pytest tests/test_phase10_properties.py \
  tests/test_phase10_verifier.py -q
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
shasum -a 256 artifacts/SHA256SUMS
```

The verifier does not import `src/phase10_search.py`. It independently
reconstructs the affine constants, gap residues, rational cycles, exact
logarithm intervals, Stern--Brocot arithmetic, all spacing layers by reverse
activation with a Fenwick tree, and every mandatory adversarial row. Tampered
gap identities, canonical ranges, margins, first-crossing rules, spacing
layers, adversarial counts, claim statuses, and cycle digests are rejected.

## P63 — gap modulus (`CONDITIONAL`)

Write

```text
P=3^q, Q=2^K, D=Q-P, d=r3-r2.
```

The exact endpoint equation gives

```text
B=D*r2+Q*d,
B=P*d (mod D),
d=B*P^(-1) (mod D).
```

The inverse exists because `gcd(P,D)=1`. Thus, with

```text
rho=[B*P^(-1)]_D, m=(B-Q*rho)/D,
```

the q0 near box has `rho=d`, `m=N`, and `X=m+rho`. Conversely these
quantities reconstruct the canonical residues when
`0<=rho<=W` and `0<m,m+rho<2^72`. The canonical-range certificate checks
`K0>72`, `q0>=46`, and `3^46>2^72`.

The verifier also reconstructs `D>W` without constructing the enormous q0
powers. If `x=K0*ln(2)-q0*ln(3)>0`, then
`D=3^q0*(exp(x)-1)>3^44*x>W`; every comparison uses rational intervals.

In the least-positive-counterexample setting, `N=1 mod 4` would give
`T^2(N)=(3N+1)/4<N`, so `N=3 mod 4`. Together with P61's `X=3 mod 4`, this
gives `4|rho`. P63 remains conditional because the near-box setting depends
on the Phase 9 least-counterexample framework and does not determine the
unknown q0 word or its affine constant `B`.

## P64 — renewal barrier (`CONDITIONAL`)

For a least-counterexample orbit point `N<=S<=N+W`, with every relevant orbit
value at least `N>V`, a coefficient first crossing must satisfy

```text
V/(V+W) <= (3+1/V)^q / 2^K.
```

The Phase 7 Stern--Brocot parents are reconstructed exactly:

```text
left      = 103768467013 / 65470613321
candidate = 114208327604 / 72057431991 = K0/q0
right     = 10439860591  / 6586818670
```

Their determinant is one, q0 is the mediant, and rational logarithm
enclosures certify

```text
left < log2(3) < K0/q0 < log2(3+1/V) < right.
```

For `q<q0`, the right-parent lattice split has either zero determinant height,
where the full parent margin is positive, or positive height, where the
`ln(2)/6586818670` unit margin is positive. Both margins strictly exceed
`ln(1+W/V)`. The `q=0` case is excluded directly. The independently checked
first-crossing rule `K=ceil(q*log2(3))` then yields

```text
S is coefficient-safe through K0-1 = 114208327603 steps.
```

Hence if `d>0`, `N` and `X=N+d` would be two distinct long-safe integers at
distance at most `W`. This conclusion retains the least-counterexample and
X02 inputs and does not exclude a q0 or later crossing.

## E15 and C05 — exact safe-pair spacing

The production scan exhausts `2<=n<=1,500,000`. Safe sets are nested, and
deleting a newly unsafe point merges its two neighboring gaps by exact
addition. The generator implements forward deletion with a neighbor heap;
the verifier independently uses reverse activation and a Fenwick tree.

The spacing records are

```text
k:      0  1  2  73  77  96  105  111  135  145  184   188
Delta:  1  2  4   8  12  16   32  228  752 1856 66688 268416
```

The deepest defined spacing in this finite prefix is

```text
Delta_213(1500000)=268416,
pair=(1126015,1394431),
stopping times=(224,214).
```

At `k=214` only one safe start remains in the scanned prefix. This is not an
infinite or larger-H lower bound. No recursive cylinder certificate scaling
to q0 was found, so

```text
C05: Delta_(K0-1)(2^72)>4142380786
```

was neither proved nor evaluated and remains `OPEN`.

The mandatory finite adversarial audit includes `2^m-1` for `m<=64`,
`8^m-5` for `m<=32`, all 4,096 twelve-block `(110|111)^*` words, and 1,024
`A^rB^s` pairs with `1<=r,s<=32`. In the last family, 713 words remain
coefficient-safe throughout the specified word and 311 have a first crossing.
Passing these bounded checks is not evidence of universality.

## P65 — formal rational-cycle lemma (`VERIFIED_THEOREM`)

For a coefficient-safe first-crossing word, `z=B/D` is fixed by the complete
formal affine composition because `D=Q-P`. At prefix `j`, exact subtraction
from `z` has numerator

```text
(3^a_j-2^j)*B+B_j*D >= 0.
```

Coefficient safety supplies the first nonnegative factor, while `B_j,D>=0`.
Therefore `z` is the minimum element of that formal rational affine cycle.
Moreover `B=P*d (mod D)` and `gcd(P,D)=1` give

```text
gcd(B,D)=gcd(d,D).
```

This is a theorem about the formal rational branches associated with the word;
it does not assert a new positive integral Collatz cycle. The finite audit
independently reconstructs both identities for all 81,118 first-crossing words
through `q=15`.

Christoffel extremality is kept separate as EXT06, an external 2026 preprint
result about rotation-class extrema. It is not reproved or used to accept P65.

## What this result does not prove

Phase 10 does not prove C04, C05, H54, H57, the existence or nonexistence of a
least counterexample, or the Collatz conjecture. It does not reprove X02 or
Christoffel extremality. The `q<=15` and `H<=1,500,000` computations cannot
establish the q0 spacing target or any eventual asymptotic statement.

## Acceptance result and SHA-256

Acceptance result: `178 passed in 210.81s`. The focused Phase 10 suite passes 8 tests,
including independent-verifier acceptance and tamper rejection.
`artifacts/phase10_verifier.json` records `valid=true`, C04 and C05 as `OPEN`,
and `proves_collatz=false`.

```text
47bbff79c5dcf1e838c05156b7b92461a4ce3ead52d593d1c87dc2944d8bdf8c  phase10_gap_modulus.json
0c639884fd662a5004ec1b3fb19774e31a583245128b518e8973d04c54774db5  phase10_obstruction_report.md
5504f03c2c8f450cae0a8aa9eca5ef2e06b8424a81e6235cb423a6cfcc867e93  phase10_rational_cycle.json
f21c14990939cf2cbedc2084672da62504395b9ffad23b43e190fc4101de9972  phase10_renewal_barrier.json
f5f3011afe30dbccf39c76a6ed059b47a374420659365d5cc49008543ef31518  phase10_safe_pair_spacing.json
f30d1c74081cbc46917c164577706937a6d04e90dd4a6577a1dad8c24b2f3041  phase10_verifier.json
```

SHA-256 of `artifacts/SHA256SUMS`:
`d9e87c0e6c1800c0fbc8376565dbeaeab39e5615b72c9fb79fffc87930dd3ae2`.
