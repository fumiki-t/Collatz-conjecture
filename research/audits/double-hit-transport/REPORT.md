# Phase 31 audit — double-hit transport

**Status:** accepted exact derivations with one global-grid repair

**Branch:** `feat/phase31-double-hit`

**Collatz conjecture:** open; `proves_collatz=false`

The supplied note was treated as an untrusted proposal. Static singleton
extraction, the double-hit factor inequality, the stronger area constant, and
the exact grid lemma survive. The proposed near-grid interpretation requires
a repair: the residual exceptional-context set can have positive density, so
area equality alone does not force global approximate shift invariance.

## 1. P185 — static singleton extraction

Fix a discrepancy-minimum reduced profile `a_0=a_q=0`, a maximum-height
index, and the unique level component through it at each height. These `h`
components form the spine. Put

\[
B_h=\sum_{r=1}^{h-1}\left\lfloor\frac r\delta\right\rfloor,
\qquad \Sigma=A-J-B_h.
\]

Every nonspine nonsingleton component consumes at least one unit of excess
length, while the spine consumes at least `B_h`. If `E` counts the spine and
all nonspine nonsingletons, then

\[
 E\le h+\Sigma.
\]

A nonspine singleton `[u,u+1)` at level `k` is necessarily its column's top
cell. Descent legality gives `a_u=k`, `a_(u+1)=k-1`, and mechanical exponent
`b_u=2`. Lowering `a_u` by one preserves legal positive exponents. Distinct
extracted cells have distinct labels and their expanded-word supports are
pairwise disjoint. Rebuilding the residual profile first and then applying
all swaps `10->01` therefore reconstructs the original word independently of
the Phase 30 level order.

The residual level components are exactly the `E` exceptional components;
the other `K=J-E` components are the extracted singleton swaps.

## 2. P186 — residual contexts and low-hit factors

For a cyclic factor width `n`, compare length-`n+2` contexts at the same
cyclic starts in the residual and mechanical words. A residual component of
mechanical span `s` can change at most `s+n+1` starts. Thus, with exact
residual span `T_res`,

\[
 |\mathcal U|\le\min\{L,T_{res}+E(n+1)\}
 \le\min\{L,2A+E(n+1)\}.
\]

Each static singleton swap influences at most `n+1` cyclic starts. Outside
`mathcal U`, a start hit zero or one time is obtained from a mechanical
length-`n+2` context using no swap or one of at most `n+1` relative swaps.
Since the rational mechanical word has at most `n+3` such contexts, the
number of low-hit factor types is at most

\[
B_1(n)=(n+2)(n+3).
\]

If all `L` cyclic length-`n` factors are distinct, at least
`L-|mathcal U|-B_1(n)` starts have two or more singleton influences. Summing
incidences and using `K=J-E` proves

\[
2L\le(J+E)(n+1)+4A+2(n+2)(n+3).
\]

The proof only needs influence sets of size at most `n+1`; it does not assume
the false equality `K(n+1)` when `n=L`.

## 3. P187 — double-hit area constant

Consider primitive positive cycles with `q->infinity`, `L/q->ell` in
`(1,2]`, and a fixed inverse-polynomial multiplier gap. If
`A/q^(2/3)` is bounded, P157/P180 give
`n_cyc=h+O(log q)` and P167 gives `h=O(q^(1/3))`.

Along a convergent subsequence write

\[
x={J\over q^{2/3}},\quad y={h\over q^{1/3}},\quad
z={\Sigma\over q^{2/3}},\quad w=x+z.
\]

Since `E<=h+Sigma`, P186 yields `wy>=2ell`. Exact coarea gives

\[
\liminf {A\over q^{2/3}}
\ge w+{y^2\over2(\ell-1)}.
\]

The unique minimum under `wy>=2ell` occurs at
`y^3=2ell(ell-1)` and proves

\[
\liminf {A\over q^{2/3}}
\ge C_{hit}(\ell)
=\frac{3(2\ell)^{2/3}}{2(\ell-1)^{1/3}}.
\]

Its cube is exactly four times P181's cube.

## 4. P188 — branch constants

The function cube `27ell^2/[2(ell-1)]` decreases on `1<ell<2`.
P163 therefore gives the internal noncritical constant

\[
C_{hit}(2)=3\,2^{1/3},
\qquad 3.779763<C_{hit}(2)<3.779764.
\]

On the critical branch P164/EXT17 gives the `ell=log_2(3)` specialization

\[
3.870329<C_{crit}<3.870330.
\]

Only this critical specialization inherits EXT17.

## 5. P189 — repaired equality structure

Convergence to the P187 frontier forces

\[
{h\over q^{1/3}}\to(2\ell(\ell-1))^{1/3},\qquad
{J+\Sigma\over q^{2/3}}
\to{(2\ell)^{2/3}\over(\ell-1)^{1/3}},
\]

and `A/(J+Sigma)->3/2`. It also forces
`E-Sigma=o(q^(2/3))`, aggregate nonspine excess beyond one per
nonsingleton component to be `o(q^(2/3))`, and leading saturation of the
P186 factor inequality and selected state-separation proxy.

Let `U` be the actual residual exceptional-context set. Outside `U`, all but
`o(L)` starts have exactly two singleton influences; the total singleton
incidence inside `U` is `o(L)`. This is local relative to `U`. Nothing here
proves `|U|=o(L)`.

## 6. P190 — exact grid identity

Let `chi_t` indicate a static swap anchor and
`c_t=sum_(r=0)^(w-1) chi_(t+r)` on a cyclic word of length `L`. Direct
cancellation gives

\[
c_{t+1}-c_t=\chi_{t+w}-\chi_t.
\]

If every `c_t=2`, the anchor word is invariant under shift `w`. With
`g=gcd(L,w)`, it is `g`-periodic and a length-`w` window contains
`(w/g)` copies of the period's anchor count. Hence `w/g` is one or two.

In general, a shift mismatch makes at least one of `c_t,c_(t+1)` differ from
two, so

\[
\#\{t:\chi_{t+w}\ne\chi_t\}
\le2\#\{t:c_t\ne2\}.
\]

## 7. NG40 — global near-grid does not follow

The accepted inequality chain permits an exact normalized equality model at
`ell=2`. Let `y^3=4` and set

\[
w=y^2,\qquad x=z=e={y^2\over2}.
\]

Then `(x+z)y=4=2ell`, `ey=2=ell`, and the sharp area value is
`3y^2/2`, but the extracted-anchor scale is `k=x-e=0`. The residual
exceptional-context set can occupy all starts. Thus P185--P189 alone do not
imply a global `o(L)` bad-window count or global approximate-grid invariance.

This is a countermodel to the proposed inference from the normalized
inequalities, not an actual positive integer Collatz cycle.

## 8. E43 — independent finite audit

The generator identifies extracted components from level sets and performs
literal disjoint swaps. The verifier independently enumerates compositions,
reconstructs reduced profiles and residual words, compares contexts at the
same starts, and regenerates all synthetic profiles. It imports no generator
code. Exact checks cover:

- 2,214 cyclic classes and 3,101 minimum rotations through `q<=8`;
- all 45,369 cyclic widths, including 27,832 distinct-factor widths;
- 1,280 extracted disjoint swaps and 8,218 exceptional components;
- 673,303 individual grid-recurrence positions and 109 exact-grid cases;
- nine legal tall, plateau, isolated, near-extremal, width-two, multipeak,
  near-grid, and residual-heavy profiles;
- 112-term generator and 176-term verifier logarithm enclosures;
- NG34--NG40, both negative controls, and every mandatory family.

Tamper tests reject corpus digests, extraction counts, constants, removed
EXT17 dependence, global-grid overclaims, NG40 changes, and Collatz
overclaims.

## 9. Remaining H172 boundary

P190 becomes useful only when the global bad-window count is small. H172 now
has a precise dichotomy:

1. grid-like: prove small bad-window count and apply a low-denominator
   pair-location resultant;
2. residual-heavy: use the positive-density minimal nonsingleton components
   and P171 endpoint binomials directly.

No strict subleading arithmetic gap is currently known in either branch.

## What this result does not prove

It does not prove a grid/residual resultant, exclude arbitrary-area positive
cycles, eliminate either nonperiodic P69 branch, or prove or disprove the
Collatz conjecture. `proves_collatz=false`.
