# Phase 14 independent audit: coalescent rewrites and H72

**Audit date:** 2026-08-27

**Base:** `origin/main` at `7e6f637cb0bed954a5f50f71a1aa6c45b127dc8f`

**Repository status:** `OPEN`

**`proves_collatz=false`**

The attached Phase 14 note was treated as an untrusted proposal.  Every
identity below was rederived from the repository's full shortcut convention.
The production generator and independent verifier use different data
structures and do not import one another.

## 1. Accepted classification

| ID | Status | Audited result |
|---|---|---|
| P81 | `VERIFIED_THEOREM` | Exact coalescent affine criterion, cylinder legality, and sign/positivity boundary. |
| P82 | `VERIFIED_THEOREM` | A least positive discrepancy-escaping permanent-safe counterexample source has only rewrite-irreducible initial renewal addresses; reducibility is a right ideal and accepted edges terminate. |
| P83 | `VERIFIED_THEOREM` | Initial-one-run companion thresholds, equality cases, and the strict general lower bound. |
| P84 | `VERIFIED_THEOREM` | Exact companion-ratio decrement and reciprocal summability over nontrivial blocks. |
| P85 | `VERIFIED_THEOREM` | Reduced moving-shadow denominator and gcd bounds for `a_n>=1`, hence eventually under P76. |
| E23 | `VERIFIED_FINITE` | Complete `Q<=13` renewal-address rewrite graph, pressure table, fixed-block collisions, finite normal forms, and 2,144 adversarial instances. |
| NG24 | `REFUTED` | Coalescent equivalence is a two-sided congruence under renewal-block concatenation. |
| P80 | `CONDITIONAL` | Status unchanged; Phase 14 does not prove either canonical anti-concentration premise. |
| H72 | `OPEN` | Status unchanged. |

## 2. Map and affine convention

For a full shortcut word `w` of length `L(w)` and odd count `Q(w)`, write

\[
F_w(x)=\frac{3^{Q(w)}x+B(w)}{2^{L(w)}}.
\]

Bits are read from left to right.  On a one at zero-based position `j`, the
correction is replaced by `3B+2^j`; a zero leaves it unchanged.  A word has
one exact source residue modulo `2^L`, and satisfying the final affine
congruence is equivalent to realizing every literal parity bit.

A renewal address is a concatenation of the forward reversals of P77's first
strict-upcrossing codewords.  Every prefix of each forward block has positive
coefficient discrepancy: a prefix is the whole positive-discrepancy block
minus a nonpositive-discrepancy proper suffix.  Concatenations are therefore
coefficient-safe.

## 3. P81 — the coalescent rewrite theorem

Let `a,d` be nonempty binary words and let `k>=0`, `m` be integers.  Comparing
the coefficient of `x` and the constant term in

\[
F_d(2^kx+m)=F_a(x)
\tag{3.1}
\]

gives

\[
\frac{3^{Q(d)}2^k}{2^{L(d)}}
=\frac{3^{Q(a)}}{2^{L(a)}}.
\]

Unique factorization of powers of two and three gives

\[
Q(a)=Q(d)=Q,
\qquad L(d)=L(a)+k.
\tag{3.2}
\]

The constant terms then agree exactly when

\[
\boxed{2^kB(a)-B(d)=m3^Q.}
\tag{3.3}
\]

Conversely, (3.2)--(3.3) directly imply (3.1).  This proves the claimed
criterion in both directions.

### 3.1 Cylinder legality

If `x` realizes `a`, then

\[
3^Q(2^kx+m)+B(d)=2^k(3^Qx+B(a))
\]

is divisible by `2^(L(a)+k)`.  Hence `2^kx+m` realizes `d`.  This is a parity
cylinder theorem, not merely equality of two real affine functions.

The sign cases remain separate:

- `m>0`, `k>=1`: every positive `x` gives a positive larger source;
- `m=0`, `k>=1`: `d` is the leading-zero lift of `a`; it is legal as a full
  parity word but not as a forward renewal address, which starts with one;
- `m<0`: positivity requires `2^kx+m>0`, and descent from the larger source
  requires `(2^k-1)x>-m`;
- `k=0`: the relation is the translation
  `B(a)-B(d)=m3^Q`.

Affine equality alone does not prove positivity, renewal legality, or
coefficient safety.

### 3.2 The minimum rewrite

The complete address universe through `Q=13` gives the first collision at
`Q=4`:

```text
a = 1 | 110 | 1 = 11101,   L=5, B=73, source=7
d = 111100,                 L=6, B=65, source=15
```

Both endpoint residues and literal endpoints equal 20, and

\[
2\cdot73-65=81=3^4.
\]

Therefore

\[
\boxed{F_{111100}(2x+1)=F_{11101}(x).}
\]

The minimum order is explicitly `(Q, larger L, smaller L, larger block
count, smaller block count, lexicographic forward words)`.  Every address of
every block count with total `Q<=13` was enumerated, so this minimum is exact
for that order and domain.

### 3.3 The fixed-three-block `Q=13` collision

The note's larger example is correct:

```text
a = 1 | 111111000 | 111110010
d = 11111111010000 | 110 | 110
```

The independent reconstructions give

```text
Q(a)=Q(d)=13
L(a)=19, L(d)=20
B(a)=2280275, B(d)=2966227
2B(a)-B(d)=1594323=3^13
```

Their least positive sources are 361,855 and 723,711, and their common least
endpoint is 1,100,380.  The supplied lifted sources

```text
x=886143, 2x+1=1772287
```

realize the two literal words and both reach 2,694,703.  The verifier hashes
the complete integer traces, rather than trusting these endpoints.

This is the only exact duplicate within any fixed block-count layer in the
complete `Q<=13` audit: it occurs at block count three.  Phase 13's zero count
was correct only through `Q<=12` and separately within each fixed block-count
layer.  It did not compare different block counts in one combined universe.

## 4. P82 — the least permanent-safe source reduction

Assume the set `C` of positive ordinary counterexample sources satisfying

\[
\Delta_n>0\quad(n>0),
\qquad \Delta_n\to+\infty
\]

is nonempty.  By well-ordering it has a least member `S`.  P77 decomposes its
word into renewal blocks.

Suppose an initial address `d` of `S` has a uniform positive downward rewrite
to another renewal address `a`.  Write

\[
S=2^kx+m,
\qquad 0<x<S,
\qquad F_d(S)=F_a(x).
\]

Then:

1. `x` is a positive ordinary integer and every prefix of `a` is
   coefficient-safe;
2. after coalescence, `x` and `S` have the same future orbit;
3. the coefficient discrepancy accumulated through `a` is that through `d`
   plus `k log 2`, so every later prefix remains safe and the discrepancy
   still tends to infinity;
4. because the common future is a counterexample, `x` is a counterexample.

Thus `x` belongs to `C`, contradicting the minimality of `S`.  Every initial
renewal address of the least member of `C` is therefore rewrite-irreducible.

EXT07/P74 conditionally supplies such a discrepancy-escaping permanent-safe
source from every nonperiodic positive counterexample.  The theorem above is
internal; that application retains the external dependency.

### 4.1 Right ideal and termination

If `d` rewrites to `a` and `b` is any common renewal suffix, then

\[
F_{db}(2^kx+m)
=F_b(F_d(2^kx+m))
=F_b(F_a(x))
=F_{ab}(x).
\]

So reducible initial addresses form a right ideal.  Every accepted finite
edge sends the least positive source of its cylinder to a smaller positive
source in the target cylinder.  The target's least positive representative
is no larger, so this representative is a strictly decreasing integer
potential.  Directed rewrite cycles are impossible.

This does not prove confluence.  A terminating rewrite graph can still have
several irreducible normal forms.

## 5. E23 — complete finite rewrite and pressure audit

The generator and verifier independently enumerate every renewal address with
total `Q<=13`, without fixing block count.

| Quantity | Exact value |
|---|---:|
| First-upcrossing codewords available in the domain | 3,331 |
| Addresses, all block counts 1--13 | 30,084 |
| `(Q,r3)` equivalence classes | 24,197 |
| Collision classes | 5,829 |
| Unordered collision pairs | 5,949 |
| Maximum class multiplicity | 4 |
| Positive downward rewrite edges | 5,949 |
| Reducible addresses | 5,887 |
| Irreducible addresses / finite normal forms | 24,197 |
| Minimal reducible prefixes | 1,656 |

Class sizes are:

```text
size 1: 18,368
size 2:  5,775
size 3:     50
size 4:      4
```

Every finite class has exactly one irreducible normal form.  No directed
cycle or nonunique normal form occurs in this domain.  This is
`VERIFIED_FINITE`, not a Church--Rosser theorem.

Every accepted edge has `m>0`; the ranges are

```text
k=1: 5,887 edges
k=2:    58 edges
k=3:     4 edges
1<=m<=7
```

### 5.1 Irreducible pressure by block depth

The following are exact sums over addresses having exactly `i` blocks and
total `Q<=13`.  Decimal strings are display-only.

| `i` | all | reducible | irreducible | `sum_irr 3^-Q` | `sum_irr 2^-L` | `sum_irr 2^-L3^-Q` |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3,331 | 684 | 2,647 | 0.484699148165083 | 0.673875808715820 | 0.180767270543173 |
| 2 | 9,089 | 1,892 | 7,197 | 0.236139728273380 | 0.456168174743652 | 0.032679624784434 |
| 3 | 4,474 | 962 | 3,512 | 0.112876750821509 | 0.304081916809082 | 0.005908385300546 |
| 4 | 4,424 | 924 | 3,500 | 0.053907520621606 | 0.202427864074707 | 0.001068297559224 |
| 5 | 3,492 | 616 | 2,876 | 0.025082746720708 | 0.132366180419922 | 0.000193171695406 |
| 6 | 2,488 | 401 | 2,087 | 0.011231726569836 | 0.084217071533203 | 0.000034931152448 |
| 7 | 1,352 | 245 | 1,107 | 0.004733670655193 | 0.050951004028320 | 0.000006316147176 |
| 8 | 739 | 108 | 631 | 0.001919937177096 | 0.029541015625000 | 0.000001141554957 |
| 9 | 418 | 45 | 373 | 0.000728208775763 | 0.016464233398438 | 0.000000205951919 |
| 10 | 196 | 10 | 186 | 0.000239600131216 | 0.008300781250000 | 0.000000036828058 |
| 11 | 67 | 0 | 67 | 0.000060840871015 | 0.003509521484375 | 0.000000006335804 |
| 12 | 13 | 0 | 13 | 0.000009408382116 | 0.000976562500000 | 0.000000000918787 |
| 13 | 1 | 0 | 1 | 0.000000627225474 | 0.000122070312500 | 0.000000000076566 |

The apparent late decay is dominated by the fixed `Q<=13` cap.  It cannot be
used to define an asymptotic `sigma_irr` or `tau_irr`.  Right-ideal closure of
finitely many forbidden prefixes changes a finite leading mass but by itself
does not improve the eventual pressure exponent.  No exact closed transfer
operator was found.

## 6. NG24 — failure of a two-sided quotient

The minimum collision has common endpoint residue 20 modulo `3^4`.  Prefix
both words on the left by the renewal block `110`:

```text
110 | 11101   has endpoint residue 263 modulo 3^6
110 | 111100  has endpoint residue 587 modulo 3^6.
```

They are no longer equivalent.  Thus endpoint coalescence is a right
congruence under a common suffix but not a left congruence under an arbitrary
common prefix.  A transfer state containing only the current coalescent class
loses information required by future left composition.  This exact
counterexample is NG24.

## 7. P83 — valuation-separated companion thresholds

Let `w` be a nontrivial forward renewal block with length `L`, odd count `q`,
and initial one-run exactly `r>=2`.  Since `u=rev(w)` first crosses strictly at
its last bit,

\[
3^{q-1}<2^{L-1},
\qquad 2^L<3^q.
\tag{7.1}
\]

The first `r` ones contribute

\[
3^q-2^r3^{q-r}
\]

to `B`.  Hence

\[
B\ge3^q\left(1-(2/3)^r\right).
\]

Using (7.1),

\[
\boxed{R(w)=\frac{B+2^L}{3^q}
>\frac53-(2/3)^r.}
\tag{7.2}
\]

For the sharper small-run constants, if `q>r`, adjacent exchanges move every
one after the mandatory zero immediately following the initial run as far left
as possible. Thus the fixed-run correction is minimized uniquely by

```text
1^r 0 1^(q-r) 0^(L-q-1),
```

with

\[
B_{r,\min}=3^q+2^r3^{q-r}-2^{q+1}.
\tag{7.3}
\]

Combining (7.3) with `2^L>2*3^(q-1)` gives, for `q>r`,

\[
R(w)>
\frac53+\left(\frac23\right)^r
-2\left(\frac23\right)^q.
\tag{7.4}
\]

For fixed `r` this lower bound is strictly increasing in `q`.  The two
upcrossing inequalities make `q=3` and `q=5` impossible.  The remaining
boundary cases are exact:

- `r=2,q=2` forces `L=3,w=110`, giving `R=13/9`; for `q>=4`,
  (7.4) is already strictly larger;
- `r=3,q=4` forces `L=6`, and (7.3) gives the unique minimizer
  `w=111010` with `R=137/81`; `q=5` is impossible, and (7.4) is
  strictly larger for `q>=6`;
- `r=4,q=4` forces `L=6,w=111100`, giving `R=43/27`; `q=5` is
  impossible, and (7.4) is strictly larger for `q>=6`;
- `r=5` starts at `q=6`, where (7.3) gives `R>=403/243>43/27`;
- `r=6,q=6` forces `w=111111000` and `R=1177/729>43/27`; for
  `q>=7`, (7.4) is strictly larger;
- for `r>=7`, the general bound (7.2) is already strictly larger than
  `43/27`.

Consequently

\[
\boxed{
\begin{array}{ll}
r=2:&R(w)\ge13/9,\quad w=110\text{ only at equality},\\
r=3:&R(w)\ge137/81,\quad w=111010\text{ only at equality},\\
r\ge4:&R(w)\ge43/27,\quad w=111100\text{ only at equality}.
\end{array}}
\tag{7.5}
\]

The `r=2` line is P79.  The strict comparisons above prove that the displayed
words are the only equality cases; no floating-point comparison is used.

The independent finite audit enumerates all 14,764 first-upcrossing words
through `Q=14`, finds no violation, and reproduces the three equality words.
That enumeration tests the proof; it is not its basis.

## 8. P84 — companion ratio decrement

For

\[
z=\frac{h-1}{S+1},
\qquad
z'=\frac{h-R}{S+R},
\]

P79 gives

\[
z-z'=\frac{(R-1)(S+h)}{(S+1)(S+R)}.
\]

On a legal nontrivial block, `h>R` and `R>=13/9`.  Therefore

\[
z-z'>\frac{R-1}{S+1}
\ge\frac4{9(S+1)}
>\frac1{3S+4}.
\]

Since `U=(S+1)/4`, this is

\[
\boxed{z-z'>\frac1{12U+1}.}
\tag{8.1}
\]

The positive decrements telescope, so on an infinite legal renewal orbit

\[
\boxed{
\sum_{i:w_i\ne1}\frac1{12U_i+1}\le z_0<\infty.}
\tag{8.2}
\]

This does not prove H72: rapidly increasing `U_i` is fully compatible with
(8.2), and no divergent lower bound for the left side is known.

## 9. P85 — qualified moving-shadow denominator bound

Use P76's positive, nonperiodic, permanently coefficient-safe odd-orbit
notation and assume reciprocal summability. For `n>=1`
put

\[
\lambda_n=\frac{2^{E_n}}{3^n}=2^{-a_n-\theta_n},
\qquad
H_n=\frac{B_n}{D_n}=\frac{b_n}{q_n},
\qquad
D_n=3^n-2^{E_n},
\]

where `b_n/q_n` is reduced and positive.  Assume `a_n>=1`.  The positive
inverse-series tail gives

\[
\frac{B_n}{3^n}<h_0,
\qquad \lambda_n<1/2,
\]

and hence

\[
0<H_n=\frac{B_n/3^n}{1-\lambda_n}<2h_0.
\tag{9.1}
\]

The exact 2-adic identity is

\[
H_n+x_0=\frac{2^{E_n}(x_n-x_0)}{D_n}.
\]

Permanent coefficient safety and the positive affine correction give
`x_n>=x_0`; nonperiodicity makes `x_n-x_0` a positive even integer. Since
`q_n` is odd, the positive integer

\[
b_n+x_0q_n=q_n(H_n+x_0)
\]

is divisible by `2^(E_n+1)`.  Combining this with (9.1) gives the strict bound

\[
\boxed{q_n>\frac{2^{E_n+1}}{x_0+2h_0}.}
\tag{9.2}
\]

With `g_n=gcd(B_n,D_n)=D_n/q_n`, (9.2) yields

\[
\begin{aligned}
g_n
&<\frac{(x_0+2h_0)D_n}{2^{E_n+1}}\\
&=\frac{x_0+2h_0}{2}\left(2^{a_n+\theta_n}-1\right)\\
&<(x_0+2h_0)2^{a_n}.
\end{aligned}
\tag{9.3}

Reciprocal summability implies `a_n->infinity`, so (9.2)--(9.3) hold for all
sufficiently large `n`.  The unqualified claim at exceptional `a_n=0`
indices is not proved or accepted by Phase 14.

These bounds still do not trigger Roth, Ridout, or the subspace theorem:
the constant is orbit-dependent, no algebraicity is known, and no
height-relative approximation exponent greater than two is obtained.

## 10. Adversarial regression

The exact convention regression contains 2,144 instances:

```text
2^m-1:          22
8^m-5:          10
(110|111)^*: 2,046
A=11101:         1
B=1100:          1
A^rB^s:         64
```

Phase 7 macro id 0 is separately reconstructed.  NG21, both NG22 models, and
NG23 are retained as interpretation boundaries, not falsely reported as
positive renewal sources rejected by rewrite.  In particular, the minimum
rewrite uses `A=11101`, but it does not eliminate the arbitrary `A^rB^s`
family or the raw-Haar obstruction.

## 11. Strategic effect on H72 and P80

Phase 14 adds a valid least-source reduction: under EXT07/P74, a hypothetical
nonperiodic counterexample supplies a least positive discrepancy-escaping
permanent-safe counterexample source, and every initial renewal address of
that source must lie in the irreducible tree.

The missing theorem is now sharper:

> Prove an all-depth recursive bound for the irreducible initial-address tree,
> while retaining enough ordinary source information to absorb the
> per-address lattice error in P80.

The finite quotient does not provide it.  Coalescent equivalence is not a
left congruence, so a state containing only `(Q,r3)` is not a closed transfer
operator.  Even an asymptotic pressure improvement would still need a sound
ordinary-representative count or an equivalent positive-height obstruction.

The most concrete next lemmas are:

1. characterize when left concatenation lifts a coalescent pair, using the
   missing 3-adic lift/carry rather than only `(Q,r3)`;
2. prove that every sufficiently large irreducible prefix must pay a uniform
   weighted loss, or construct the smallest high-pressure irreducible family;
3. combine the eventual P85 denominator bound with rewrite irreducibility to
   control the reduced odd denominator, rather than applying a generic
   Diophantine theorem directly.

## 12. What this result does not prove

- It does not prove global confluence or a canonical normal form at every
  odd count.
- It does not prove an asymptotic `sigma_irr` or `tau_irr`.
- It does not prove either premise of P80.
- It does not exclude every positive ordinary permanent-safe source or prove
  H72.
- It does not exclude nontrivial positive cycles.
- It does not prove or disprove the Collatz conjecture.

`proves_collatz=false`.
