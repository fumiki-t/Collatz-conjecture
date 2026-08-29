# Phase 17 audit — predecessor pressure and the 270 dichotomy

## 1. Result and scope

This audit treats `phase17_predecessor_pressure_note.md` as an untrusted
research proposal. It accepts a four-odd-step predecessor sieve, an exact
nonperiodic finite-crossing dichotomy, an exponent-code pressure identity,
and a suffix-decodable finite block code after the repairs below. It also
records a ceiling for one deliberately restricted Haar-envelope method.

The shortcut map is

\[
T(n)=n/2\quad(n\equiv0\pmod2),\qquad
T(n)=(3n+1)/2\quad(n\equiv1\pmod2).
\]

P104--P106 are `VERIFIED_THEOREM`, E28--E29 are `VERIFIED_FINITE`, NG29 is
`REFUTED`, and H104/H105 remain `OPEN`. No external theorem is used. In
particular, finite enumeration is not promoted to an asymptotic result and
`proves_collatz=false`.

## 2. Repairs and acceptance boundaries

Three boundaries in the proposal require explicit qualification.

First, for an accelerated inverse word the affine correction is positive.
Therefore an endpoint is forbidden already at equality `y/N=c`, not merely
when `y/N<c`. The stored mod-648 table nevertheless admits a residue class at
its exact threshold. This makes the table a safe right-continuous *upper
envelope* for allowed classes, not the exact boundary set.

Second, endpoint cylinders for different exponent words can overlap. The
pressure identity is exact for the first-passage word probabilities, but a
sum of 3-adic cylinder measures is only an upper bound for their union. No
lower union-measure or ordinary-representative count is inferred.

Third, the r=4 code proves suffix decodability for every number of blocks, but
the audited pressure value at one finite block size proves no convergence or
monotonicity of pressure roots.

## 3. Accelerated inverse words

Let `e=(e_1,...,e_r)` be positive odd-to-odd exponents and `E=sum e_i`. If
`x` is the source odd value and `y` the endpoint after these `r` accelerated
steps, direct induction gives

\[
2^E y=3^r x+A(e),
\]

where

\[
A(e)=\sum_{j=0}^{r-1}3^{r-1-j}2^{e_1+\cdots+e_j}
\]

and the empty exponent sum at `j=0` is zero. Hence

\[
y=c(e)(x+\beta(e)),\qquad
c(e)=\frac{3^r}{2^E},\qquad
\beta(e)=\frac{A(e)}{3^r}>0.
\]

Integrality is equivalent to the endpoint congruence

\[
y\equiv A(e)2^{-E}\pmod{3^r},
\]

whose residue is a 3-adic unit. If `N` is the least positive counterexample,
`y` lies on its orbit, `c(e)>1`, and `y<=c(e)N`, then the positive integral
inverse source satisfies

\[
x=y/c(e)-\beta(e)<N.
\]

It shares the future of `y`, contradicting least positivity. This proves the
height-conditioned exclusion, including equality.

## 4. E29 — exact r<=4 sieve

Every positive composition with `r<=4` and `3^r>2^E` is enumerated. There are
exactly 23 exponent words. Lifting their endpoint congruences to the 54 unit
classes modulo 81 gives the following maximum-multiplier distribution.

| maximum multiplier | unit classes |
|---:|---:|
| `81/16` | 1 |
| `27/8` | 2 |
| `81/32` | 3 |
| `9/4` | 5 |
| `27/16` | 4 |
| `3/2` | 15 |
| `81/64` | 2 |
| `9/8` | 5 |
| none | 17 |

Intersecting with P99's odd-even-even exclusion modulo 8 yields the
right-continuous allowed-class upper envelope modulo 648:

```text
threshold:  1  9/8  81/64  3/2  27/16  2  9/4  81/32  27/8  81/16
classes:   51   66     72  117    129 172  192     204   212     216
```

The continuous normalized capacity below `81/16` is

\[
C_4=\frac{23093}{20736}.
\]

Above it, the continuous cutoff holding normalized count `t=q/N` is

\[
U(t)=3t+\frac{11899}{6912}.
\]

For decreasing `1/x`, charging the first point in each allowed residue class
to the interval's left endpoint and integrating the rest gives the exact
finite-lattice error

\[
1+\sum_I\frac{\#R_I}{u_I}=\frac{18344}{27}.
\]

The initial `1` is the possibly non-unit tail minimum. Distinctness of the
odd inputs is essential.

## 5. P104 — exact 270 dichotomy

Let `Psi_4(t)` be the reciprocal integral of the mod-648 envelope. At
`t=270`, the cutoff is

\[
U(270)=\frac{5610619}{6912}.
\]

The verifier reduces every logarithm to `[1,2)` by exact powers of two and
uses 12 terms of

\[
\log z=2\sum_{j=0}^{11}\frac{w^{2j+1}}{2j+1}+R,
\qquad w=\frac{z-1}{z+1},
\]

with the positive geometric tail bound. It reconstructs the total removed
`log 2` coefficient `7/3` and proves, using no floating-point decision,

\[
\Psi_4(270)+\frac{18344}{27\cdot300000}<3\log2.
\]

E28 independently proves that every `1<=n<300000` reaches 1. Thus a least
positive counterexample has `N>=300000`. If its finite coefficient first
crossing has `q` distinct odd inputs and `t=q/N<=270`, then either `t` is below
the sieve capacity and the elementary `Y_q<=N+q/3` bound applies, or the
monotone packing bound above applies. In both cases

\[
Y_q<2N.
\]

P98 then makes the crossing word and every safe prefix shortest in its exact
same-Q safe endpoint class. This is branch G270.

For `t>270`, only the final density-`1/3` interval changes, so

\[
\frac{Y_q}{N}<
2\left(\frac{U(t)}{U(270)}\right)^{1/9}.
\]

The right side divided by `t` is strictly decreasing because

\[
\frac{d}{dt}\log\frac{U(t)^{1/9}}t
=\frac{1}{3U(t)}-\frac1t<0.
\]

Consequently branch H270 satisfies

\[
N<\frac q{270},\qquad
Y_q<\frac q{135},\qquad
X<\frac q{135},\qquad
Z=2X<\frac{2q}{135}.
\]

P104 is an exhaustive dichotomy only under its named least-counterexample,
finite-crossing, and distinct-odd-input hypotheses. It does not apply to a
repeated periodic segment.

## 6. E28 — direct finite audit

Literal shortcut iteration for every `1<=n<300000` gives:

```text
sources checked:                  299999
all reach 1:                      true
maximum shortcut stopping steps: 278 (least source 230631)
maximum orbit peak:               12324038948 (least source 270271)
ascending row SHA-256:            573dba321ea39a77547fe3202a74d26b
                                  f37b988628fd7567b9ae2924f6d62ed2
```

The generator scans sources upward. The independent verifier fills its orbit
memo in descending source order, then serializes the exact rows upward for the
digest. This proves only the stated finite range.

## 7. P105 — exponent-code pressure identity

Give every positive exponent probability

\[
p_e=\frac3{4^e},\qquad \sum_{e\ge1}p_e=1.
\]

For a word of length `r` and exponent sum `E`,

\[
p(w)=\frac{3^r}{4^E}=3^{-r}c(w)^2.
\]

The logarithmic coefficient walk has positive mean because

\[
\mathbb E\log c=\log3-\frac43\log2>0,
\]

and the sign is the exact comparison `27>16`. A direct Chernoff estimate
avoids invoking a strong law: for `2m` exponents,

\[
\Pr\!\left(\sum e_i\ge3m\right)\le(243/256)^m.
\]

Therefore `c_(2m)>(9/8)^m` eventually almost surely, so the first-passage code
`F_t` is a probability-one partition. Only exponent `e=1` can cross upward,
and its factor is `3/2`; hence `t<=c(w)<3t/2`. Exact optional stopping is not
needed beyond summing the disjoint probability cylinders, which gives

\[
\sum_{w\in F_t}3^{-|w|}c(w)^2=1,
\qquad
\frac4{9t^2}<\sum_{w\in F_t}3^{-|w|}\le\frac1{t^2}.
\]

The second display is a raw sum over word cylinders. Endpoint residues can
collide, so only its upper bound transfers automatically to union measure.

## 8. NG29 — scoped Haar-envelope ceiling

NG29 refutes only this explicitly defined proposed mechanism:

1. forbid an endpoint solely when a predecessor word has `c>=u`;
2. estimate deletion solely by summed 3-adic Haar cylinder mass;
3. discard affine `beta`, the fixed positive ordinary source, transition
   dependence, canonical representatives, and carry.

Even granting collision-free maximal deletion, the deletion density after
intersecting odd integers is at most `1/(2u^2)`. The deliberately optimistic
remaining-density envelopes are

\[
A_{\min}(U)=\frac{U-1}{3}-\frac12(1-1/U),
\]

\[
R_{\min}(U)=\frac13\log U-\frac14(1-1/U^2).
\]

Near `u=1` the formal deletion can exceed the baseline density; retaining
that over-deletion only makes the proposed mechanism look stronger. Exact
12-term log enclosures locate the root of `R_min(U)=3log2` in

\[
1083.903<U<1083.904.
\]

At the upper endpoint,

\[
A_{\min}(U)=\frac{12209787721}{33872000}<360.469.
\]

Thus this coefficient-only summed-Haar envelope cannot push its normalized
cutoff arbitrarily far. This is not a theorem that geodesicity, predecessor
sieving, affine-aware methods, or fixed-source arithmetic must fail.

## 9. P106 — suffix-decodable r=4 code

Among supercritical four-exponent words, choose the shortest total exponent
for each endpoint residue modulo 81, breaking ties lexicographically. The
result has 11 codewords and exact `s=2` moment

\[
\sum_{w\in C}3^{-4}c(w)^2=\frac{1539}{2048}.
\]

For a concatenation, its endpoint modulo 81 is the endpoint residue of the
last block, so the last codeword is unique. If its affine data are `(E,A)`,
the preceding endpoint residue is recovered exactly by

\[
\frac{2^E y-A}{3^4}.
\]

Repeating proves suffix decodability for any finite block count. The finite
audit separately enumerates 11, 121, and 1,331 addresses at one, two, and
three blocks and finds the same number of distinct endpoint residues. Neither
this count nor the single moment establishes an all-depth pressure trend.

## 10. Open obligations

- H104: exclude the G270 positive ordinary-source all-prefix geodesic branch.
- H105: exclude the H270 two-sided box while retaining source, endpoint,
  literal safety, signed carry, and periodic separation.
- The nontrivial-cycle branch remains separate.
- Phase 17 does not settle the permanent-safe H72 branch.

## 11. What this result does not prove

Phase 17 does not exclude G270/H104, H270/H105, a nontrivial cycle, H89, H72,
or any Collatz counterexample. It does not convert finite tables, Haar volume,
or a finite code moment into an asymptotic ordinary-integer theorem.

`proves_collatz=false`.
