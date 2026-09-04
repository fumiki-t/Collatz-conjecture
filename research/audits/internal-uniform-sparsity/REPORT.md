# Phase 37 independent audit: internal uniform orbit sparsity

## 1. Scope and status

The supplied Phase 37 v2 note was treated as an untrusted proposal.  This
audit checks its parity-vector recursion independently and separates the
all-scale proof from bounded diagnostics.  No Garcia--Tal or Heppner theorem
is used in P219--P226.

| ID | Status | Audited conclusion |
|---|---|---|
| P219 | `VERIFIED_THEOREM` | Fixed-odd-count corrections have an exact maximum, and their images of any translated interval have a location-independent diameter. |
| P220 | `VERIFIED_THEOREM` | Equal-time collision-free positive sets obey `G(X)=O_rho(X^rho)` for every `rho>H_2(1/log_2 3)`; in particular `G(X)<32X^(29/30)`. |
| P221 | `VERIFIED_THEOREM` | Uniform dyadic tail moments, including reciprocal summability, follow for `rho_*<rho<1`. |
| P222 | `VERIFIED_THEOREM` | Every non-eventually-periodic positive shortcut orbit has discrepancy tending to infinity and an odd permanent coefficient-safe suffix minimum. |
| P223 | `VERIFIED_THEOREM` | Its odd defects have a uniform `O(2^(rho A))` small-defect count, a convergent defect sum, and the stated density-one improvement. |
| P224 | `VERIFIED_THEOREM` | At renewal boundaries `h_i=O(S_i^rho)` and `(h_i-1)/(S_i+1)->0`. |
| P225 | `VERIFIED_THEOREM` | Renewal minima have consecutive limsup ratio at most `3/2`. |
| P226 | `VERIFIED_THEOREM` | Every noncritical primitive positive cycle has minimum below an effective finite cutoff. |
| E53 | `VERIFIED_FINITE` | Independent exact finite reconstruction of the induction boundary, affine corpus, translations, orbit products, renewal conventions, and adversarial controls. |
| H70, H72, H133 | `OPEN` | Their mathematical statements are not proved. P222 removes H70 as a necessary global route for ordinary nonperiodic orbits, but does not prove H70 itself. |

The conjecture remains `OPEN`; `proves_collatz=false`.

## 2. Map and quantifiers

Throughout,

\[
T(x)=\begin{cases}
x/2,&x\equiv0\pmod2,\\
(3x+1)/2,&x\equiv1\pmod2.
\end{cases}
\]

A positive set `P` is **equal-time collision-free** when distinct `x,y` in
`P` satisfy `T^r(x) != T^r(y)` for every integer `r>=0`.  For integer
`X>=1`, define

\[
G(X)=\sup_{P,a}\#(P\cap[a,a+X)),
\]

where `a>=1` is an integer and the supremum is over all such positive sets.
The interval is half open.  Trivially `G(X)<=X`.

Any subset of an equal-time collision-free set remains so.  If `A` is such a
subset, then `T^N(A)` is also equal-time collision-free: an equal-time
collision after `r` more steps would be a collision of the original points
after `N+r` steps.  This closure property is the essential reason the
recursion below is valid.

The distinct points of a primitive orbit form such a set.  The distinct
points of a non-eventually-periodic orbit do as well: if `i<j` and
`T^r(x_i)=T^r(x_j)`, the deterministic orbit repeats with period `j-i` from
time `i+r` onward.

## 3. P219: fixed-count affine diameter

Let a literal length-`N` parity vector have ones at

\[
0\le p_1<\cdots<p_s<N.
\]

Induction over its bits gives

\[
T^N(x)=\frac{3^s x+B_v}{2^N},\qquad
B_v=\sum_{i=1}^s3^{s-i}2^{p_i}.
\tag{3.1}
\]

Every summand increases when its position moves right.  Under strict ordering
the unique maximizing positions are `p_i=N-s+i-1`.  Therefore

\[
\begin{aligned}
B_v&\le\sum_{i=1}^s3^{s-i}2^{N-s+i-1}\\
&=2^{N-s}(3^s-2^s).
\end{aligned}
\tag{3.2}
\]

The same argument places the unique minimum at `p_i=i-1`, with
`B_min=3^s-2^s`; only the upper bound is needed later.

Let `x` range over any `[a,a+X)` with `X<=2^N`.  At fixed `s`, (3.1)--(3.2)
put every image, across every parity vector of that weight, inside one real
interval of length less than

\[
\frac{3^sX}{2^N}+\frac{2^{N-s}(3^s-2^s)}{2^N}
\le 3^s+(3/2)^s<2\,3^s.
\tag{3.3}
\]

The integer images consequently fit in a half-open integer interval of
length `2*3^s`.  Its location may depend on `a`, but its length does not.

Finally, the congruence

\[
3^s x+B_v\equiv0\pmod {2^N}
\]

has one solution because `3^s` is a unit modulo `2^N`.  The standard
intermediate induction shows this is exactly the parity cylinder.  Hence a
length-`X<=2^N` interval contains at most one source for each vector.

## 4. P220: uniform interval sparsity

Set

\[
\alpha=\log_2 3,\qquad
\rho_*=H_2(1/\alpha).
\]

First take `rho_*<rho<1`.  Continuity and strict decrease of binary entropy
on `(1/2,1)` allow a

\[
1/2<\theta<1/\alpha
\quad\text{with}\quad H_2(\theta)<\rho.
\tag{4.1}
\]

For an integer `X>=2`, put `N=ceil(log_2 X)`, so
`2^(N-1)<X<=2^N`.  Split the sources by their number `s` of odd bits during
the first `N` steps.

For fixed `s<=theta*N`, P219 and the image-closure observation in Section 2
give at most `G(2*3^s)` points.  In the high part there is at most one source
per parity vector.  The deterministic entropy count is

\[
\sum_{s>\theta N}{N\choose s}\le2^{NH_2(\theta)}.
\tag{4.2}
\]

For completeness, (4.2) follows by weighting each high word with
`t^s>=t^(theta*N)` for `t=theta/(1-theta)>1` and expanding `(1+t)^N`.
It is only a count of binary words; no random-orbit model is assumed.  Thus

\[
G(X)\le
\sum_{0\le s\le\lfloor\theta N\rfloor}G(2\,3^s)
+2^{NH_2(\theta)}.
\tag{4.3}
\]

Since `alpha*theta<1`, every recursive argument is below `X` once `X` is
large.  Under the strong-induction hypothesis `G(Y)<=C Y^rho`, the low sum is
`O(C X^(rho*alpha*theta))`, while the high term is `O(X^H2(theta))`.
Both exponents are strictly below `rho`.  Choose an effective finite base so
the first term uses at most half the desired allowance, then enlarge `C` to
cover the base and the high term.  This proves

\[
G(X)=O_\rho(X^\rho).
\tag{4.4}
\]

For `rho>=1`, (4.4) follows already from `G(X)<=X`, completing the claimed
quantifier `rho>rho_*`.

### 4.1 Explicit rational certificate

Take

\[
\theta=14/23,\qquad\rho=29/30.
\]

The two strict exponent comparisons are exactly

\[
3^{14}<2^{23},\qquad
23^{690}<2^{667}14^{420}9^{270}.
\tag{4.5}
\]

The second is `H_2(14/23)<29/30` after multiplying by 690 and exponentiating
base two.  Because `14/23<1/alpha` and entropy decreases here, it also proves
`rho_*<29/30<1` without a decimal decision.

An explicit induction closes with

\[
\boxed{G(X)<32X^{29/30}}\qquad(X\ge1).
\tag{4.6}
\]

Here are all constants.  Put `N0=135`.  Recursive arguments are smaller for
all `N>=57`; after raising to the 23rd power the sufficient inequality is

\[
4^{23}3^{14N}<2^{23N}.
\]

Let `k=floor(14N/23)`.  Since `3^rho>2`,

\[
\sum_{s=0}^k(2\,3^s)^\rho
<6\,3^{\rho\theta N}.
\]

The exact sufficient condition making the low part less than
`(32/2)X^rho` is

\[
24^{690}3^{406N}\le2^{667N}.
\tag{4.7}
\]

It first holds at `N=135` and then persists because
`3^406<2^667`; it fails at `N=134`.  The high part is below
`2^(rho*N)<2X^rho` by (4.5).  Thus the induction step is below
`18X^rho<32X^rho`.  For `N<135`, the trivial bound works because
`X<=2^134<32^30`, hence `X<32X^(29/30)`.  Every comparison in this paragraph
is reconstructed as an integer inequality by the independent verifier.

## 5. P221: tail moments

Fix `p>rho>rho_*`.  On the dyadic shells
`[2^r S,2^(r+1)S)`, P220 gives at most `C_rho(2^rS)^rho` points.  Therefore

\[
\sum_{\substack{x\in P\\x\ge S}}x^{-p}
\le C_\rho S^{\rho-p}
\sum_{r\ge0}2^{-r(p-\rho)}
=C_{\rho,p}S^{\rho-p}.
\tag{5.1}
\]

For reciprocal summability one must, and can, choose
`rho_*<rho<1` and `p=1`.  This quantifier is made explicit here because later
limits use the negative exponent `rho-1`.

## 6. P222: internal permanent-safe reduction

Let `(x_n)` be a non-eventually-periodic positive integer orbit, and let
`q_n` count odd full-shortcut steps before time `n`.  Its orbit set is
equal-time collision-free, and the sequence is injective.  P221 gives

\[
\sum_{n\ge0}\frac1{x_n}<\infty.
\tag{6.1}
\]

Multiplying the exact factors at every step gives

\[
x_n=x_0\frac{3^{q_n}}{2^n}
\prod_{\substack{0\le j<n\\x_j\text{ odd}}}
\left(1+\frac1{3x_j}\right).
\tag{6.2}
\]

The product converges to a finite positive limit by (6.1).  An injective
sequence of positive integers tends to infinity: below any fixed height there
are only finitely many available integers.  Taking logarithms in (6.2)
therefore proves

\[
\Delta_n=q_n\log3-n\log2\longrightarrow+\infty.
\tag{6.3}
\]

The sequence `Delta_n` has a global minimum.  It is unique, since equality
at two distinct times would imply equality of nontrivial powers of 2 and 3.
Let its time be `t`.  If `x_t` were even then
`Delta_(t+1)=Delta_t-log 2`, a contradiction, so `x_t` is odd.  For every
`n>t`,

\[
3^{q_n-q_t}>2^{n-t}.
\tag{6.4}
\]

The affine correction of the prefix starting at the odd `x_t` is positive,
so (6.4) also gives `x_n>x_t`.  Thus `x_t` is an odd strict suffix minimum of
the actual orbit and every nonempty future prefix has coefficient greater
than one.

Consequently an actual positive Collatz counterexample has only two global
possibilities:

1. an eventually periodic nontrivial positive cycle; or
2. a nonperiodic orbit with a permanent coefficient-safe tail.

This is an internal replacement for the ordinary-orbit conclusion previously
available conditionally through EXT07/P74.  EXT07 and P74 remain valid
historical entries and an independent external route.  P222 does not prove
the mathematical spacing statement H70; it makes that route unnecessary for
the global nonperiodic dichotomy.

## 7. P223: internal small-defect count

At the odd accelerated tail, P72 writes

\[
x_j=2^{a_j+\vartheta_j}Y_j,
\qquad0\le\vartheta_j<1,
\]

where (6.1) makes `Y_j` converge to a finite `Y_infinity`.  If `a_j<=A`, then
`x_j<2^(A+1)Y_infinity`.  P220, applied to this subset of the same orbit,
gives for every `rho>rho_*`

\[
\#\{j:a_j\le A\}=O_{x_0,\rho}(2^{\rho A}).
\tag{7.1}
\]

Choose `rho<1`.  Summing the number of indices in successive unit defect
shells against `2^-A` proves

\[
\sum_j2^{-a_j}<\infty,
\qquad a_j\to\infty.
\tag{7.2}
\]

If `c<1/rho_*`, choose `rho_*<rho<1/c`.  Among `j<=J`, every violation of
`a_j>c log_2 j` lies in `a_j<=c log_2 J`; (7.1) bounds their number by
`O(J^(rho*c))=o(J)`.  Hence

\[
a_j>c\log_2j
\]

on a density-one set.  This is not a pointwise eventual lower bound.

## 8. P224--P225: renewal-boundary control

Let `t_i` be P77's successive strict suffix minima of discrepancy,
`S_i=x_(t_i)`, and let `h_i>1` be P76's negative-real companion.  By the same
affine argument used after (6.4),

\[
x_n>S_i\qquad(n>t_i).
\tag{8.1}
\]

Choose `rho_*<rho<1`.  P221 on this orbit suffix gives

\[
u_i:=\sum_{\substack{n\ge t_i\\x_n\text{ odd}}}\frac1{3x_n}
=O(S_i^{\rho-1}).
\]

The companion product is

\[
h_i=S_i\left[
\prod_{\substack{n\ge t_i\\x_n\text{ odd}}}
\left(1+\frac1{3x_n}\right)-1\right].
\tag{8.2}
\]

Since the product is at most `exp(u_i)` and `u_i->0`,

\[
h_i=O(S_i^\rho),\qquad
\frac{h_i-1}{S_i+1}=O(S_i^{\rho-1})\to0.
\tag{8.3}
\]

For the next renewal block `w_i`, put

\[
c_i=3^{Q_i}/2^{L_i}\in(1,3/2],\qquad
R_i=(B_i+2^{L_i})/3^{Q_i}.
\]

P79's exact companion legality is `R_i<h_i`, and direct affine algebra gives

\[
S_{i+1}+1=c_i(S_i+R_i).
\tag{8.4}
\]

Thus

\[
S_{i+1}+1<\frac32(S_i+h_i)
=\frac32S_i+O(S_i^\rho).
\]

Since `S_i->infinity` and `rho<1`,

\[
\limsup_{i\to\infty}\frac{S_{i+1}}{S_i}\le\frac32.
\tag{8.5}
\]

The standard eventual iteration of (8.5) gives
`S_i=O_epsilon((3/2+epsilon)^i)` for every `epsilon>0`.

## 9. P226: noncritical-cycle consequence

The distinct states of a primitive positive cycle are equal-time
collision-free.  If `m` is its minimum and
`lambda=3^q/2^L`, P221 yields, for `rho_*<rho<1`,

\[
\log(1/\lambda)
=\sum_{x\text{ odd in the cycle}}
\log\left(1+\frac1{3x}\right)
\le C''_\rho m^{\rho-1}.
\tag{9.1}
\]

For a noncritical cycle `lambda<1/2`, the left side is greater than `log 2`.
Because `rho-1<0`, (9.1) places `m` below an effective finite constant
`M_rho`.  There are consequently only finitely many candidate integer minima.
This does not itself give a period bound or a terminating finite orbit audit.
The audit also does not optimize `C_rho` into a useful numerical cutoff, and
it does not address critical cycles.

Negative cycles are retained only as convention regressions; positivity is
essential in P219--P226.

## 10. E53 finite and independent audit

The generator and independent verifier use different enumeration paths.  The
verifier imports no generator or `src` module.  It reconstructs:

- the exact `N0=135` induction boundary, including failure at `N=134`;
- all 131,070 binary words through `N<=16`, their unique parity residues, and
  all 152 fixed-weight extrema;
- 180 translated intervals through `N<=12`, including starts above `2^200`,
  49,928 sources, and 854 fixed-weight image-diameter groups;
- 209,868 affine/product steps from starts `1<=x<=4096`;
- 154 first-upcrossing codewords through length 16, 84 finite addresses, 228
  suffix-minimum boundaries, and 154 exact companion transitions;
- all mandatory adversarial families, source 167, and trivial/negative cycle
  controls.

The rational-shadow and P206/P218 orientation distinctions are retained as
scope boundaries in the artifact and repository documentation; they are not
misreported as newly recomputed Phase 37 finite rows.

These finite checks audit conventions and implementations only.  The
all-scale result is the proof in Sections 3--4, not extrapolation from E53.

## 11. Literature and dependency boundary

EXT07 records the Garcia--Tal interval theorem with Heppner's quantitative
input.  P74/P75 correctly remain `CONDITIONAL` on that external theorem.  The
new P219--P223 argument independently reproves the particular uniform power
sparsity, reciprocal summability, permanent-safe, and defect consequences
needed here, with a weaker explicit exponent than any unrecorded optimal
external constants.  No literature-wide novelty claim is made.

P72, P76--P79, P84--P86 remain inputs only where cited.  NG22 is untouched:
its coherent formal 2-adic source is not a positive ordinary orbit, so P220
does not apply to it.  P80 still asks for multiplicity control across many
renewal addresses; P220 controls points on one equal-time collision-free set.

## 12. What this result does not prove

- It does not give an eventual pointwise lower bound for every defect.
- It does not prove P80's canonical-address anti-concentration.
- It does not extinguish the P81/P86 irreducible renewal tree.
- It does not exclude a positive permanent-safe nonperiodic orbit or prove
  H72.
- It does not exclude critical or arbitrary-area positive cycles or prove
  H133.
- It does not prove H70 as a standalone spacing statement.
- It does not prove or disprove the Collatz conjecture.

`proves_collatz=false`.
