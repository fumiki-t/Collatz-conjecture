# Phase 11: renewal ladder — run results

Branch: `feat/phase11-renewal-ladder`

Base commit: `4baf4e1c746fea9815dfe5555e2167d44d30da00`

Phase 11 reduces a nonperiodic counterexample to an infinite ladder of tail
minima unless an infinite coefficient-safe tail occurs. It formulates the
corresponding dropping-safe pair barrier, audits it exactly through `q=4961`,
proves a height-free no-go, and adds an exact affine-margin pair-cylinder
closure. It does not prove or disprove the Collatz conjecture.
`proves_collatz=false`.

## Reproduction commands

```bash
.venv/bin/python src/phase11_search.py \
  --artifact-dir artifacts --q-limit 4961 \
  --pair-bound 262144 --pair-depth 12 \
  --gap-cap 64 --direct-bound 16384
.venv/bin/python verifier/verify_phase11.py \
  --artifact-dir artifacts --output artifacts/phase11_verifier.json
.venv/bin/python -m pytest -q tests/test_phase11_properties.py \
  tests/test_phase11_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
.venv/bin/python scripts/research_health.py
(cd artifacts && shasum -a 256 -c SHA256SUMS)
shasum -a 256 artifacts/SHA256SUMS
```

The verifier does not import the generator. It independently rebuilds `H_q`,
every dropping time through the maximum required height, all 4,961 barrier
rows, the universal height-free witnesses, the affine cylinder intervals, a
literal pair cross-check, and the mandatory adversarial digest.

## P69 — counterexample trichotomy and renewal ladder

**Status:** `VERIFIED_THEOREM`

For an orbit `x_0,x_1,...`, define a tail minimum as the minimum of a suffix.
On a nonperiodic positive integer orbit there are infinitely many successive
distinct tail minima `S_i`: a repeated value would produce a cycle, and after
the unique occurrence of one suffix minimum has passed, the next suffix has a
strictly larger minimum. Hence

```text
S_0 < S_1 < S_2 < ... .
```

Every future iterate of `S_i` is at least `S_i`. An even value immediately
halves, while for `S>1`, `S=1 mod 4` gives

```text
T^2(S)=(3S+1)/4<S.
```

Therefore every tail minimum of a counterexample satisfies

```text
S_i = 3 mod 4.
```

Here `q_i` means the number of odd shortcut steps; it is not claimed that the
integer `q_i` is odd. If the coefficient first crosses below one after `K`
steps and `q` odd steps, then

```text
K=K_q=bitlength(3^q),
D_q=2^K-3^q>0,
T^K(S)=(3^q*S+B)/2^K=S+d.
```

Coefficient safety before the crossing gives, for the position `p_r` of the
`r`-th odd step, `2^p_r<=3^r`. Thus

```text
B/3^q=(1/3)*sum_r 2^p_r/3^r <= q/3
```

and `B<=B_q^max`. Since a tail minimum has `d>=0`,

```text
B=D_q*S+2^K*d,
S<=B/D_q<=H_q.
```

Because `3^q/2^K<1`, exact rearrangement gives

```text
d < B/3^q <= q/3,
d <= floor((q-1)/3).
```

The next tail minimum is no larger than this future endpoint, so

```text
4 <= S_(i+1)-S_i <= d_i <= floor((q_i-1)/3).
```

The lower bound 4 follows from the strict increase and the common residue
`3 mod 4`. Since the integer sequence `S_i` is unbounded while the finitely
many values `H_q`, `q<=Q`, have a finite maximum, `q_i` tends to infinity.

For the formal rational fixed point `B/D_q`,

```text
gcd(B,D_q)=gcd(d,D_q)
```

because `B=D_q*S+2^K*d` and `D_q` is odd. Its reduced denominator is therefore

```text
D_q/gcd(d,D_q) > 3D_q/q,
```

using `0<d<q/3`. This is formal rational-cycle arithmetic, not a positive
integer cycle claim.

As a regression of this symbolic position argument, both implementations
independently enumerate all 4,403 coefficient-safe first-crossing words through
`q=12` and reconstruct `B<=B_q^max` and `3B<=q*3^q`. P69 is proved by the
general inequalities above, not inferred from this finite enumeration.

Every counterexample consequently lies in exactly one of the proof obligations

1. a nontrivial cycle;
2. a nonperiodic orbit with an infinite coefficient-safe tail starting at a
   tail minimum;
3. a nonperiodic finite-crossing renewal ladder satisfying the inequalities
   above.

## P70/H70 — dropping-safe pair barrier

**Statuses:** `P70 VERIFIED_THEOREM`, `H70 OPEN`

Define

```text
D_k(H)={n:2<=n<=H and T^j(n)>=n for 1<=j<=k}.
```

`Delta_down_k(H)` is the minimum difference of two distinct members, with
value `+infinity` when fewer than two members exist. If, for every sufficiently
large q,

```text
Delta_down_Kq(floor(H_q)+floor((q-1)/3))
  > floor((q-1)/3),
```

then no finite-crossing renewal ladder exists. Indeed, `q_i` eventually enters
the asserted range; both `S_i` and `S_(i+1)` belong to the displayed
dropping-safe set and height, but their gap is at most the forbidden bound.
P70 is this exact implication; H70 is the still-unproved eventual inequality.

This is a weaker counterexample reduction than asking C05 to settle the full
Phase 10 q0 coefficient-safe spacing target. It is not a pointwise claim that
dropping-safe spacing is easier: `D_k(H)` is a larger set than the analogous
coefficient-safe set. Nontrivial cycles and infinite coefficient-safe tails
remain separate proof obligations.

## E18 — exact audit through q=4961

**Status:** `VERIFIED_FINITE`

The generator and verifier independently reconstruct every numerical input.
Neither takes the expected failure list or the final height as an axiom.

```text
q range:                 1..4961
maximum required height: 1,666,251
maximum dropping time:   224 at n=1,126,015
failure q:               17,22,27,29,32,34
least pair at each fail: (27,31), gap 4
pass range:               every 35<=q<=4961
q=4961:                  K=7863, floor(H_q)=1,664,598,
                         allowance=1,653, height=1,666,251
```

| q | K_q | height | allowance | members | Delta | pair | result |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 17 | 27 | 113 | 5 | 8 | 4 | `(27,31)` | fail |
| 22 | 35 | 64 | 7 | 4 | 4 | `(27,31)` | fail |
| 27 | 43 | 51 | 8 | 3 | 4 | `(27,31)` | fail |
| 29 | 46 | 290 | 9 | 5 | 4 | `(27,31)` | fail |
| 32 | 51 | 46 | 10 | 2 | 4 | `(27,31)` | fail |
| 34 | 54 | 114 | 11 | 2 | 4 | `(27,31)` | fail |
| 35 | 56 | 30 | 11 | 1 | `+infinity` | — | pass |
| 4961 | 7863 | 1666251 | 1653 | 0 | `+infinity` | — | pass |

The first structurally vacuous case is `q=141`: from that point `K_q` is at
least 224, the largest dropping time found anywhere in the scanned maximum
height. Thus later finite passes mostly record an empty set, not positive
evidence for an eventual spacing theorem.

## NG20 — height-free spacing (`REFUTED`)

For every integer `k>=3`, the two integers

```text
2^k-5,  2^k-1
```

are k-step dropping-safe and differ by 4. The right orbit has the closed form

```text
T^j(2^k-1)=3^j*2^(k-j)-1.
```

Writing `j=3r+s`, the left orbit has

```text
s=0: 9^r*2^(k-3r)-5
s=1: 3*9^r*2^(k-3r-1)-7
s=2: 9^(r+1)*2^(k-3r-2)-10.
```

Each expression is at least its start for `0<=j<=k`. Therefore no
height-free global spacing bound can exceed 4 at any depth. Ordinary height is
an essential variable. The verifier checks the symbolic forms and a direct
regression through `k=256`.

## P71/E19 — exact affine-margin pair cylinders

**Statuses:** `P71 VERIFIED_THEOREM`, `E19 VERIFIED_FINITE`

On a fixed length-L parity cylinder `x=r+2^L*t`, write

```text
T^j(x)=(3^a_j*x+B_j)/2^j.
```

The dropping margin is

```text
T^j(x)-x=((3^a_j-2^j)*x+B_j)/2^j,
```

an exact affine function of t with integer slope

```text
(3^a_j-2^j)*2^(L-j).
```

For positive slope its minimum is at the lower t endpoint; for negative slope
it is at the upper endpoint. Intersecting all inequalities from both tails
therefore produces one exact integer interval of pair parameters. Affine states
compose by

```text
0: (A,B,Q) -> (A,B,2Q)
1: (A,B,Q) -> (3A,3B+Q,2Q).
```

Production audit:

```text
H=262,144, L=12, gap<=64
represented integer pairs: 16,775,072
nonempty input cylinders:   262,144
dropping-safe pairs:        48,822
all-safe cylinders:         763
empty-safe cylinders:       261,381
partial cylinders:          0
```

A literal audit independently checks 523,728 pairs through `H=16,384`, depth
12 and gap 32. The mandatory families contribute 5,156 adjacent-pair margin
checks.

This is a genuine recursive interval closure, not a raw depth extension.
However, it retains all `2^L` residue classes. No cross-cylinder dominance is
proved, and NG19 forbids silently replacing the L-bit residue by a literal
shorter window at `L=12`. The eventual Phase 11 certificate is not found.

## Tamper rejection

Tests require rejection after changing:

- the P69 theorem status, P70 implication, or H70 open status;
- the E18 failure list or NG20 status;
- the P71 transition rule;
- the E19 cylinder digest;
- the scalability boundary.

The tests also assert that the verifier imports no generator module.

## What this result does not prove

Phase 11 does not prove the eventual dropping-safe pair barrier, eliminate a
nontrivial cycle, eliminate an infinite coefficient-safe tail, prove C04,
C05, H54, or the Collatz conjecture. Finite empty-set passes cannot be promoted
to an asymptotic statement. The pair-cylinder rule is exact but not yet a
bounded-size automaton.

## Acceptance and SHA-256

Full suite: `193 passed in 217.84s`.

Focused Phase 11 and health suite: `6 passed in 21.17s`.

```text
a6fba47df5a6e7726207c65daa259d3d26cc4964a0a1ef09eb25f50fd443eb5a  phase11_renewal_ladder.json
d074e4852ab6329db1ad660c741bc199f43d2e21009f812c4d4af6fa1d39dc1d  phase11_dropping_pair_audit.json
de726bdb3a44fd0e9a2d8fc03b6484a47addd33b084bf0e289c0f4811fac1dd0  phase11_pair_cylinder.json
2348c616c4d74042a858a0c59074cb6a59cbc149739a80344eaccb3d73ecaeea  phase11_obstruction_report.md
ea9c40ab8b9e62333ef2fad958bfbdab02a9f1cd526032ac6283fa4ccff45651  phase11_verifier.json
```

SHA-256 of `artifacts/SHA256SUMS`:
`085ec7d66263db348e1b49bfbe3adec26b785b9ee58d09b6b03cda1957f329e3`.
