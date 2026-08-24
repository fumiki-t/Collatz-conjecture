# Phase 12: infinite-safe-tail odd-orbit packing — run results

Branch: `feat/phase12-infinite-safe-packing`

Base commit: `851c82b49455ba1fa91a756bb0f300ea94c311c9`

Phase 12 proves a polynomial upper envelope and an octave-defect packing law
for the infinite coefficient-safe-tail branch of P69.  It also rules out the
single all-contact mechanical word as a positive-integer infinite orbit.  It
does not exclude arbitrary infinite safe tails or prove the Collatz
conjecture. `proves_collatz=false`.

## Reproduction commands

```bash
.venv/bin/python src/phase12_search.py \
  --artifact-dir artifacts --start-bound 100000 \
  --max-odd 96 --contact-q 512
.venv/bin/python verifier/verify_phase12.py \
  --artifact-dir artifacts --output artifacts/phase12_verifier.json
.venv/bin/python -m pytest -q tests/test_phase12_properties.py \
  tests/test_phase12_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
.venv/bin/python scripts/research_health.py
(cd artifacts && shasum -a 256 -c SHA256SUMS)
shasum -a 256 artifacts/SHA256SUMS
```

The verifier does not import the generator.  It reconstructs the exact
normalization on ordinary shortcut orbits, every finite audit row, all 2,144
mandatory adversarial instances, all 512 mechanical prefixes and canonical
residues, and the 4,096-row packing obstruction.

## P72 — odd-orbit packing theorem

**Status:** `VERIFIED_THEOREM`

Assume `S` is a tail minimum of a nonperiodic positive-integer orbit and every
coefficient prefix from `S` is safe.  Let `x_j=T^(d_j)(S)` be its j-th odd
iterate, so `d_0=0`, and define

```text
theta_j = fractional_part(j*log2(3)),
a_j     = floor(j*log2(3))-d_j,
Y_j     = 2^d_j*x_j/3^j.
```

Coefficient safety at time `d_j` gives `a_j>=0`.  Direct substitution gives

```text
x_j=2^(a_j+theta_j)*Y_j.
```

If `e_j=v2(3x_j+1)`, then `d_(j+1)=d_j+e_j` and

```text
Y_(j+1)
 =2^(d_j+e_j)*[(3x_j+1)/2^e_j]/3^(j+1)
 =Y_j*(1+1/(3x_j)).
```

Thus

```text
log(Y_j/S)
 =sum_(i<j) log(1+1/(3x_i))
 <=(1/3)sum_(i<j)1/x_i.
```

### Residue packing

Nonperiodicity makes all `x_i` distinct.  For `i>=1`,

```text
x_i=(3x_(i-1)+1)/2^e
```

is odd and nonzero modulo 3, hence `gcd(x_i,6)=1`.  Every complete block of
six integers contains exactly two values coprime to six.  If the post-initial
values are sorted as `z_0<z_1<...`, then

```text
z_r>=S+3(r-1)  for r>=2.
```

The initial value and the first two packed values cost at most `3/S`; the
remaining decreasing sum is bounded by its integral:

```text
sum_(i<j)1/x_i
 <=3/S+sum_(r=1)^(j-3) 1/(S+3r)
 <=3/S+(1/3)log(1+3j/S).
```

Consequently,

```text
Y_j<=S*exp(1/S)*(1+3j/S)^(1/9).
```

This is an Archimedean consequence of actual odd-value distinctness.  It is
not inferred from the finite audit.

### Octave-defect count

If `a_i<=A`, then `0<=theta_i<1` and monotonicity of `Y_i` give

```text
x_i<2^(A+1)*Y_i<=2^(A+1)*Y_j.
```

Up to a real height `X`, there are at most `2+X/3` positive integers coprime
to six.  Allowing the exceptional initial iterate gives

```text
#{i<j:a_i<=A}
 <=3+[2^(A+1)*S*exp(1/S)/3]*(1+3j/S)^(1/9).
```

For `0<epsilon<8/9`, set
`A=floor((8/9-epsilon)log2(j))`.  The right side is
`O(j^(1-epsilon))=o(j)`.  At `epsilon=8/9`, the `A=0` bound is
`O(j^(1/9))`; for larger epsilon the claim is immediate from `a_i>=0`
apart from finitely many initial indices.
Therefore for every `epsilon>0`,

```text
a_i>(8/9-epsilon)*log2(i)
```

holds on a density-one set of positive indices.

This is a density statement about the index set, not a pointwise lower bound.

### Finite first crossing

After q odd inputs and K total shortcut steps,

```text
T^K(S)=(3^q/2^K)*Y_q.
```

At coefficient first crossing, `3^q/2^K<1`.  Writing
`T^K(S)=S+d` therefore gives the strict exact comparison

```text
d<Y_q-S
 <S*[exp(1/S)*(1+3q/S)^(1/9)-1].
```

The production audit checks the stronger rational comparison
`T^K(S)<Y_q` before using any transcendental display bound.

## P73 — all-contact mechanical word

**Status:** `VERIFIED_THEOREM`

The choice `a_j=0` at every odd index has positions

```text
d_j=floor(j*log2(3)).
```

Equivalently, its parity word is the upper mechanical word of slope
`alpha=ln(2)/ln(3)`.  The slope is irrational because `2^p=3^q` has no
positive integer solution, so the word is aperiodic.  If a positive integer
realized the whole word, P72 with `A=0` would give

```text
j<=3+C_S*j^(1/9),
```

which is impossible as `j` tends to infinity.  Every finite prefix still has
one exact canonical residue modulo `2^K`; the artifact reconstructs this
through 512 odd inputs.  Local 2-adic realizability is therefore not silently
confused with an infinite positive-integer orbit.

## Literature-overlap audit

- Lagarias (1985) records the lower parity-one density
  `ln(2)/ln(3)` for an integer trajectory tending to infinity.
- Monks–Yazinski (2004), Theorem 2.7(b), extends the lower-density restriction
  to divergent rational 2-adic orbits.
- López–Stoll (2009) studies the conjugacy map over Sturmian words.  Their 2021
  preprint states that a divergent rational 2-adic orbit must have lower
  parity-one density equal to the critical value and explicitly studies
  critical mechanical words.

Phase 12 does not claim the critical density or the mechanical-word language
as new.  P72 instead packs the distinct positive odd values and bounds the
distribution of `a_i`.  No claim of literature-wide novelty is made, and none
of these external results is used to accept P72 or P73.

Primary records:

- [Lagarias, *The 3x+1 problem and its generalizations*](https://doi.org/10.2307/2322189)
- [Monks–Yazinski, *The autoconjugacy of the 3x+1 function*](https://doi.org/10.1016/S0012-365X(03)00125-0)
- [López–Stoll, *The 3x+1 Conjugacy Map over a Sturmian Word*](https://doi.org/10.1515/INTEG.2009.014)
- [López–Stoll 2021 preprint](https://arxiv.org/abs/2101.12747)

## E20 — exact finite orbit audit

**Status:** `VERIFIED_FINITE`

The production run audits every `S=3 mod 4` through 100,000:

- 25,000 starts;
- all terminate their recorded safe prefix at a coefficient first crossing;
- maximum recorded prefix: 85 odd iterates, first at `S=35655`;
- minimum exact `Y_q-T^K(S)` is `14/9`;
- 2,144 mandatory adversarial instances, including all requested families;
- longest adversarial prefix: 90 odd iterates at normalized start 67,108,863
  in `(110|111)^*`.

These values are regenerated rather than treated as axioms.  They test the
identities and conventions only; no finite orbit is evidence against an
infinite safe tail.

## NG21 — why the exponent did not improve

**Status:** `REFUTED`

The hypothesis that distinctness, a fixed lower bound, and
`gcd(x_i,6)=1` alone imply `Y_j=O(j^gamma)` for some `gamma<1/9` is false.
List every positive integer coprime to six and impose the same product
recurrence.  There are exactly two entries per six-number block, so

```text
sum 1/x_i=(1/3)log(j)+O(1),
log(1+1/(3x))=1/(3x)+O(1/x^2),
log Y_j=(1/9)log(j)+O(1).
```

This abstract saturator is not a Collatz orbit.  It proves only that a stronger
exponent needs transition congruences or another orbit-specific input.  H72
records that open target; no claim is made that `1/9` is dynamically optimal.

## Tamper rejection

Tests require rejection after changing:

- the P72 status, exponent, counting bound, density consequence, or literature
  boundary;
- the P73 status or finite mechanical-prefix digest;
- the E20 orbit or adversarial digest;
- the NG21 or H72 status and the packing-obstruction digest.

The test suite also asserts that the verifier imports no generator module.

## What this result does not prove

Phase 12 does not exclude the full infinite coefficient-safe-tail branch of
P69.  It rules out only one all-contact word and imposes a density-one octave
constraint on every surviving tail.  It does not eliminate nontrivial cycles,
prove H70, eliminate the renewal ladder, prove C04/C05/H54, or prove the
Collatz conjecture.

## Acceptance and SHA-256

Full repository suite: `199 passed in 276.25s`.

Focused Phase 12 and research-health suite: `7 passed in 8.44s`.

```text
79e48a861c00809569eae6275621122fc9794a907d47d2ddb2986f86db75a4e5  phase12_all_contact.json
3ca29a062f15a9cfd8d9b03011686973bcefed45522614ac0cc0634e064a7193  phase12_finite_orbits.json
77d77b46968d77ca90fce9866b2feb60069de62773aef74b2a95ccefef6904c5  phase12_obstruction_report.md
51b9e795057c79e81fd761088b413edd7d5a1c186c83e23cac73bae088b94cab  phase12_packing_obstruction.json
2e24adc8dd0b6b5ec6aa251992103735d7d39ee0e22eca5ea79a7835067df6e7  phase12_packing_theorem.json
109dac620c1c8eeb6c6b41b0dcca3b159b744c24d0b4653f702fbe5191c33cc7  phase12_verifier.json
```

SHA-256 of `artifacts/SHA256SUMS`:
`17f7a3ecd7783156a8ad3263e31d12e7ef8121fb71909f3fed4f3ac5e8c95d9e`.
