# Phase 28 audit — transport dispersion

**Date:** 2026-08-30
**Branch:** `feat/phase28-transport-dispersion`
**Status:** accepted exact theorem/finite audit after correction
**`proves_collatz=false`**

## 1. Scope and conventions

This report audits the supplied Phase 28 note as a proposal rather than an
authority.  Let `q>=2`, `q<L<=2q`, `p=L-q`, and let

\[
 b_j=\left\lfloor{(j+1)p\over q}\right\rfloor-
     \left\lfloor{jp\over q}\right\rfloor\in\{0,1\}.
\]

For a cyclic positive exponent composition `e=(e_0,...,e_(q-1))` of `L`, put
`a_0=0` and `a_(j+1)=a_j+b_j-(e_j-1)`.  The discrepancy-minimum rotation is
the rotation for which all `a_j>=0` and `a_q=0`.  The profile statistics are

\[
 A=\sum_{j=0}^{q-1}a_j,\quad h=\max a_j,\quad
 J=\sum_j(a_{j+1}-a_j)_+=\sum_j(a_j-a_{j+1})_+.
\]

All cyclic indices and intervals in this report use these reduced-slope
coordinates.  P133's least-value rotation remains a different coordinate;
Phase 28 does not assume they coincide.

## 2. Exact transport (`P166 VERIFIED_THEOREM`)

The baseline word has a zero at precisely the `p` indices where `b_j=1` and a
one otherwise.  Since

\[
 e_j-1=b_j+a_j-a_{j+1},
\]

every positive increment of `a` deletes that many baseline zero tokens and
every negative increment inserts that many.  The latter increments are always
`-1`, because `b_j<=1` and `e_j>=1`.  Cyclic telescoping proves that exactly
`J` zero tokens are deleted and exactly `J` are inserted.  Thus the exponent
word is obtained from the mechanical baseline by a balanced `2J`-boundary
edit script.

An edited cyclic word has at most `2J` exceptional boundaries.  Splitting a
length-`n` factor at those boundaries leaves at most `2J+1` mechanical
pieces, and the mechanical baseline has one factor per start coordinate.
The exact finite consequence is

\[
 p_{\rm cyc}(n)\le (2J+1)n+1.
\]

Combining this factor count with P125's 2-adic separation and P133's positive
cycle height bound yields the corresponding transport state-separation
inequality.  This is necessary structure, not a cycle exclusion.

## 3. Level inventory and descent density (`P167 VERIFIED_THEOREM`)

For `k>=1`, let `I_k={j:a_j>=k}` and let `U_k` be its number of cyclic
connected components.  Counting upcrossings and level cells gives the exact
coarea identities

\[
 J=\sum_{k=1}^h U_k,\qquad A=\sum_{k=1}^h |I_k|.
\]

Write `delta=p/q=(L-q)/q`.  Before a path can descend from level `h` to zero,
its `r`-th unit descent requires at least `floor(r/delta)` preceding baseline
zero opportunities.  Summing over the nested levels, with the component
entry cells removed, gives

\[
 A-J\ge \sum_{r=1}^{h-1}\left\lfloor {r\over\delta}\right\rfloor.
\]

This improves the leading triangular cost when `delta<1`, but it is not
strictly stronger at every finite nonzero profile; NG37 records the smallest
equality obstruction.

## 4. Sharp area optimization (`P168 VERIFIED_THEOREM`)

Suppose a hypothetical sequence of primitive positive cycles has
`L/q -> ell` with `1<ell<=2` and an inverse-polynomial multiplier gap.  The
P166 factor/state-separation argument gives asymptotically

\[
 \ell\le2xy,
 \qquad x={J\over q^{1/3}},\quad y={h\over q^{1/3}},
\]

while P167 gives, for every bounded subsequence of `A/q^(2/3)`,

\[
 {A\over q^{2/3}}\ge y+{x^2\over2(\ell-1)}+o(1).
\]

The first constraint is tight at the minimum.  Substitution
`y=ell/(2x)` leaves a strictly convex one-variable problem whose unique
stationary point satisfies `x^3=ell(ell-1)/2`.  Hence

\[
 \liminf {A\over q^{2/3}}
 \ge C(\ell):={3\ell^{2/3}\over
 2^{5/3}(\ell-1)^{1/3}}.
\]

No floating-point comparison is used.  The verifier reconstructs rational
cubes and independent logarithm enclosures.

## 5. Cycle branches and rigidity

`P169 VERIFIED_THEOREM`.  The cube of `C(ell)` is

\[
 {27\ell^2\over32(\ell-1)},
\]

whose derivative has sign `ell(ell-2)` on `1<ell<2`.  The noncritical branch
therefore has the internal limiting constant at least `C(2)=3/2`.  On the
critical branch, P163/P164 and external theorem EXT17 restrict `ell` to the
critical logarithmic slope and give the sharper exact rational enclosure

\[
 1.535941<C_{\rm crit}<1.535942.
\]

Only this critical specialization retains EXT17 as an external dependency.

`P170 VERIFIED_THEOREM`.  Near equality forces convergence to the unique
optimizer:

\[
 J/q^{1/3}\to(\ell(\ell-1)/2)^{1/3},\quad
 h/q^{1/3}\to(\ell^2/(4(\ell-1)))^{1/3}.
\]

It also forces normalized P167 descent slack to vanish and P166's factor/state
separation inequality to saturate.  This is a rigidity prerequisite for a
future obstruction, not such an obstruction itself.

## 6. Multilevel polynomial (`P171 VERIFIED_THEOREM`)

Let `Q_a(X)` be the reduced profile polynomial obtained after imposing
`X^q=2`.  Decomposing `a_j=sum_(k<=a_j)1` expresses `Q_a` as a sum of dyadic
endpoint binomials, one for each component of `I_k`.  It follows exactly that

\[
 |\operatorname{supp}Q_a|\le2J+1.
\]

The note's proposed `l1` estimate omitted the cost of an interval ending at
the reduced endpoint.  The correct bound is

\[
 \|Q_a\|_1\le 1+2\sum_{k=1}^h2^{k-1}U_k+
 (2^{a_{q-1}}-1).
\]

NG38 stores the first exact obstruction to the uncorrected statement.  The
decomposition and support bound survive the repair.

## 7. Refuted proposal statements

### NG37 — universal finite strict improvement

For `q=3,L=5,e=(3,1,1)`, the exact profile is `(0,1,0,0)` and
`A=J=h=1`, `delta=2/3`.  Both the old triangular and new descent-density
bounds equal one.  Thus “strictly stronger for every finite nonzero profile”
is false; the asymptotic leading-coefficient improvement remains valid.

### NG38 — endpoint-free `l1` bound

For `q=2,L=4,e=(3,1)`, the profile is `(0,1,0)` and
`Q_a=(3,-1)`.  Its `l1` norm is four, whereas the proposed endpoint-free
right side is three.  The corrected endpoint term is one and gives equality.

## 8. Exact finite audit (`E40 VERIFIED_FINITE`)

The generator enumerates all positive-`D` cyclic exponent classes through
`q<=8`; the verifier independently reconstructs them by recursive reverse
compositions.  It checks 2,214 cyclic classes, 3,101 minimum rotations,
179,606 density intervals, 45,369 factor widths, and 3,101 transport and
polynomial identities.  Five exact legal synthetic profiles separately test
tall, long-plateau, isolated-excursion, near-extremal, and seven-grid shapes.

All mandatory families are retained.  In particular `A^1B^1=111011100` and
`A^2B^3` are audited rather than replaced by the newer cycle corpus.

## 9. Independence and acceptance boundary

The verifier does not import `src/phase28_search.py`.  It uses recursive
reverse compositions, direct boundary subtraction, integer factor encodings,
transition-count level sets, independent profile synthesis, and an 88-term
logarithm enclosure in place of the generator's 72-term routine.  Tamper tests
reject corpus, constant, external-dependency, endpoint-correction,
strictness-obstruction, and overclaim mutations.

H172 remains `OPEN`: convert the near-extremal scales and sparse multilevel
polynomial into a nonzero resonance/resultant obstruction valid for all gcd
classes and both rotations.  H133 also remains `OPEN`.

## What this result does not prove

Phase 28 does not exclude a tall, diffuse, or near-extremal positive cycle; it
does not prove H172 or H133; and it does not address the nonperiodic
counterexample branches.  It does not prove or disprove the Collatz
conjecture.  `proves_collatz=false`.
