# Phase 27 audit — asymptotic cycle area and support

## 1. Outcome and convention

The supplied Phase 27 note was treated as an untrusted proposal.  The shortcut
map and accelerated odd map are

\[
T(x)=\begin{cases}(3x+1)/2,&x\text{ odd},\\x/2,&x\text{ even},\end{cases}
\qquad
x_{j+1}=(3x_j+1)/2^{e_j},\quad e_j\ge1.
\]

For a primitive positive nontrivial cycle, let `q` be the number of odd
states, `L=sum e_j`, and `lambda=3^q/2^L<1`.  Phase 26 supplies the
reduced-slope profile `a_j`, area `A_*=sum a_j`, height `h_*=max a_j`, and
the state-separation inequality P157.  This audit accepts P162--P165 as exact
theorems in their stated domains, imports Matveev's logarithmic-form theorem
as EXT17, records a bounded exact audit as E39, and refutes one rotation
shortcut as NG36.  H133 remains open.

## 2. P162 — a polynomial multiplier gap forces area dispersion

Write `alpha=log_2 3`.  Suppose a sequence of primitive positive nontrivial
cycles has `q -> infinity` and, for fixed `c>0` and `kappa>=0`,

\[
\lambda(1-\lambda)\ge c q^{-\kappa}.
\tag{2.1}
\]

P157 and P156 give

\[
\alpha q < (A_*+1)\left[
  h_*+4+\log_2\frac{q}{3\lambda(1-\lambda)}
\right],
\qquad
h_*\le\sqrt{2A_*}.
\tag{2.2}
\]

Under (2.1), the logarithmic term is at most
`(kappa+1)log_2 q+O_(c,kappa)(1)`.  On any subsequence on which
`A_*/q^(2/3)` is bounded, divide (2.2) by `q` and pass to the lower limit.
The logarithmic part vanishes and

\[
\alpha\le\sqrt2\left(\liminf\frac{A_*}{q^{2/3}}\right)^{3/2}.
\]

If the ratio is unbounded the conclusion is immediate.  Thus

\[
\boxed{\displaystyle
\liminf_{q\to\infty}\frac{A_*}{q^{2/3}}
\ge \left(\frac{(\log_2 3)^2}{2}\right)^{1/3}.}
\tag{2.3}
\]

This is a necessary asymptotic condition on a hypothetical sequence of
cycles, not an exclusion of such a sequence.

## 3. P163 — the noncritical gap is internal

P134 gives, at the least odd cycle value `m`,

\[
\log(1/\lambda)
\le \frac1m+\frac19\log(1+3q/m).
\tag{3.1}
\]

Every positive nontrivial odd cycle value is at least three.  Therefore

\[
\lambda\ge e^{-1/3}(1+q)^{-1/9}.
\]

On the noncritical branch `lambda<1/2`, so `1-lambda>1/2` and

\[
\lambda(1-\lambda)>rac12e^{-1/3}(1+q)^{-1/9}.
\tag{3.2}
\]

Equation (3.2) has the form required by P162.  No external Diophantine
estimate is used for the noncritical branch.

## 4. EXT17 and P164 — critical two-logarithm specialization

EXT17 is E. M. Matveev's explicit lower bound for a nonzero real linear form
in logarithms of algebraic numbers.  It is an external theorem, not reproved
here.  Specialize its standard real multiplicative form to

\[
\Xi=2^L3^{-q}-1>0,
\qquad \alpha_1=2,\quad\alpha_2=3,
\qquad b_1=L,\quad b_2=-q.
\]

Here the number field has degree one and `L<2q`.  The paper's two-logarithm
coefficient is bounded, using only exact majorants, by

\[
1.4\,30^5 2^{9/2}\log2\log3<K,
\qquad K=1,564,920,000,
\]

because

\[
5K=7\cdot30^5\cdot23\cdot2,
\quad 2^9<23^2,
\quad \log2\log3<2.
\]

Also `1+log(2L)<log(12q)`, using `e<3` and `L<2q`.  The specialization
therefore gives the deliberately loose but explicit bound

\[
\Xi>(12q)^{-K}.
\tag{4.1}
\]

On the critical line `L=ceil(q log_2 3)`, one has `0<Xi<1` and
`lambda=1/(1+Xi)`.  Hence

\[
\lambda(1-\lambda)=\frac{\Xi}{(1+\Xi)^2}
>\frac1{4\,12^K}q^{-K}.
\tag{4.2}
\]

P162 applies to (4.2), while P163 covers the noncritical branch.  Consequently
every hypothetical sequence of primitive positive nontrivial cycles with
`q -> infinity` obeys (2.3).  This is P164.  The huge `K` makes (4.2) useful
asymptotically but much weaker at finite heights than Phase 26's EXT05 bound.

## 5. P165 — arbitrary-gcd support dispersion

Define

\[
s_*=\#\{0\le j<q:a_j>0\}.
\]

The actual and repeated reduced-mechanical binary words have the same number
of ones.  Moving each of the `s_*` displaced labelled ones changes at most two
binary positions, so their cyclic Hamming distance is at most `2s_*`.
A changed binary position affects at most `n` cyclic length-`n` factors.
The repeated rational mechanical baseline has at most `n+1` such factors.
Thus, for every `1<=n<=L`,

\[
p_{\rm cyc}(n)\le(2s_*+1)n+1.
\tag{5.1}
\]

Since `a_(j+1)-a_j>=-1` and the closed profile descends from `h_*` to zero,
at least one positive entry occurs at every level; hence

\[
h_*\le s_*.
\tag{5.2}
\]

Repeat P157's ordinary-state separation with (5.1).  Under any fixed
polynomial multiplier gap this yields

\[
\alpha q\le(2s_*+1)
\left[s_*+O(\log q)\right]+O(1).
\]

The same bounded-subsequence argument as in Section 2 gives

\[
\boxed{\displaystyle
\liminf_{q\to\infty}\frac{s_*}{\sqrt q}
\ge\sqrt{\frac{\log_2 3}{2}}.}
\tag{5.3}
\]

P163 and P164 supply the required gap on both branches.  The proof uses the
reduced-slope baseline and therefore covers arbitrary `gcd(q,L)`.

## 6. E39 — exact finite reconstruction

The generator and verifier separately reconstruct every positive-`D` cyclic
exponent class through `q<=8`:

- 2,214 cyclic classes, 2,186 primitive classes;
- 204 critical and 2,010 noncritical classes;
- 1,417 noncoprime classes;
- 3,101 minimum-profile rotations;
- 3,101 Hamming/height support checks and 45,369 factor checks;
- eight exact tall/diffuse synthetic profiles;
- seven mandatory adversarial family rows.

The effective-envelope artifact also reconstructs the Phase 26 internal
`A_*>100000` endpoint and the conditional X02 `A_*>5*10^15` endpoint.  Six
critical Matveev-envelope rows are only sanity data; no finite theorem is
inferred from them.

The verifier imports no Phase 27 production code.  It uses recursive reverse
compositions, integer-encoded factor sets, direct `Fraction` traces, 84-term
logarithm boxes rather than the generator's 72 terms, and independently
synthesized profiles.  Tamper tests alter a corpus digest, the Matveev
constant, EXT17's status, every field of the rotation obstruction, and the
Collatz flag; all mutations must be rejected.

## 7. NG36 — rotation-alignment trap

The two rotations used in earlier phases solve different optimization
problems.  P133 starts a positive cycle at its least ordinary odd value;
P156 starts after a minimum of the reduced discrepancy walk.  They cannot be
identified formally.

The smallest positive rational affine-cycle counterexample is `e=(1,3)`:

\[
\frac57\longmapsto\frac{11}7\longmapsto\frac57.
\]

The least-value offset is zero, whereas the unique discrepancy-minimum offset
is one.  This refutes universal alignment for positive rational shadows.  It
does **not** refute a possible additional alignment theorem for positive
ordinary integer cycles; that narrower question remains open.

## 8. Structural phase diagram

P164 forces `A_*=Omega(q^(2/3))`, but this alone has two qualitatively
different survivors:

- **tall:** `h_*` is comparable with `q^(1/3)` or larger, so the profile must
  descend through many levels;
- **diffuse:** `h_*=o(q^(1/3))`, so the required area is distributed over many
  lower defects.

The synthetic exact profiles show that both shapes satisfy the abstract
reduced-profile constraints.  They are not cycles.  Future H133 work must add
an ordinary-source, correction-loss, carry, or resultant invariant that
excludes both regimes rather than assuming one.

## 9. External-input boundary

- EXT17 is used only for the critical polynomial gap in P164.  Its theorem is
  not internally reproved.
- P163 is internal and independent of EXT17 and EXT05.
- E28 is used only in finite Phase 26 envelope reconstruction.
- X02 remains external evidence and only controls the conditional comparison.
- E39 is bounded evidence and is not the proof of P162--P165.

## What this result does not prove

Phase 27 does not exclude arbitrary-area cycles, the tall or diffuse branch,
positive-integral rotation alignment, either nonperiodic counterexample
branch, or the Collatz conjecture. `proves_collatz=false`.
