# Phase 40 independent audit: normalized height and Bellman geodesics

**Audit date:** 2026-09-05

**Base commit:** `93b2c7f937d0a28fc43aee33f23786249dfa0e8d`

**Repository status:** `OPEN`
**`proves_collatz=false`**

The supplied Phase 40 note is a research proposal, not an accepted proof.
The arguments below reconstruct its normalized-height and predecessor
claims with explicit map, positivity, and infinite-versus-finite conventions.

## 1. Scope, claims, and repairs

| ID | Status | Result |
|---|---|---|
| P242 | `VERIFIED_THEOREM` | Finite normalized height on a positive nonperiodic odd orbit, its coalescent scaling identity, and attainment of a minimum within a permanent-safe shared-future class. |
| P243 | `VERIFIED_THEOREM` | A normalized-height minimizer has globally maximal prefix coefficient among positive literal competitors. Consequently H112 would exclude every positive nonperiodic orbit, without X02. |
| P244 | `VERIFIED_THEOREM` | Shortest-predecessor redundancy is bounded, nondecreasing, and eventually constant; finite normalized-height descent gives an all-prefix same-Q-geodesic representative. |
| P245 | `VERIFIED_THEOREM` | The exponent-shortened predecessor cloud of a positive nonperiodic orbit is positive, integral, and equal-time collision-free. |
| P246 | `VERIFIED_THEOREM` | For every real p greater than rho_star, the all-step valuation moment is summable; this is a direct P221/transition corollary. |
| NG43 | `REFUTED` | Greater tail weight at a fixed shifted-DAG vertex need not preserve safety after reducing the initial run. |
| E56 | `VERIFIED_FINITE` | Exact bounded Bellman, complete tail-minimality, cloud, and adversarial reconstruction. |
| H112, H72 | `OPEN` | No infinite nonzero-lift theorem or permanent-safe positive-source exclusion is proved. |

The label on P243 applies to the logical implication from H112, not to H112
or to an unconditional exclusion of nonperiodic orbits. P240 remains a valid
historical `CONDITIONAL` X02-based route. No status promotion of P240 is
needed to record the new internal reduction.

The necessary repairs to Parts I--II of the proposal are:

1. Normalized height must be defined for every coalescing positive odd
   nonperiodic source. An intermediate odd endpoint need not itself be
   permanent-safe.
2. Odd-endpoint shortestness must be connected explicitly to every full
   shortcut prefix and to the canonical endpoint classes used by H112.
3. The Bellman definition needs an empty-set convention and a separate
   zero-step case.
4. A safe replacement with redundancy one has exactly half the normalized
   height. The general descent factor is therefore **at most** one half;
   strict improvement beyond one half is available in the unsafe-valley case.
5. Eventual stabilization supplies no effective last-jump index or certified
   stopping rule. Finite descent is an existence argument, not a completed
   algorithm for recognizing its final source.

The shortcut map throughout is

\[
T(n)=\begin{cases}n/2,&n\equiv0\pmod2,\\
(3n+1)/2,&n\equiv1\pmod2.
\end{cases}
\]

A literal parity word records the input parity at each step. For a word
`w` of length `L` and odd count `q`, write

\[
F_w(z)=\frac{3^qz+B_w}{2^L},\qquad c(w)=3^q/2^L.
\]

Every nonempty prefix of a coefficient-safe word has coefficient strictly
greater than one. No nonempty prefix can have coefficient exactly one,
by unique factorization. An odd accelerated step of exponent `e>=1` is
the full shortcut word `10^(e-1)`, whose endpoint is odd; its exponent is
the exact valuation `v2(3x+1)`.

## 2. P242: normalized height and coalescent scaling

Let `x=x_0` be any positive odd source whose forward orbit is not eventually
periodic. Permanent safety is not required in this paragraph. Its successive
odd states and exact accelerated exponents satisfy

\[
2^{e_j}x_{j+1}=3x_j+1,\qquad
E_n=\sum_{j<n}e_j,\qquad c_n=3^n/2^{E_n}.
\]

There are infinitely many odd steps: an infinite positive integer trajectory
cannot consist eventually only of division by two. P221/P222 give
`sum_j 1/x_j<infinity`. The two exact finite normalizations are

\[
Y_n:=\frac{x_n}{c_n}
=x+\beta_n,
\qquad
\beta_n=\sum_{j<n}\frac{2^{E_j}}{3^{j+1}},
\tag{2.1}
\]

and

\[
Y_n=x\prod_{j<n}\left(1+\frac1{3x_j}\right).
\tag{2.2}
\]

The product converges because its logarithm is bounded by
`(1/3) sum_j 1/x_j`. Every correction term is positive. Consequently

\[
\boxed{\mathcal Y(x):=\lim_nY_n=x+\beta_\infty\in(x,\infty).}
\tag{2.3}
\]

In particular, the inverse-coefficient correction series converges by
(2.1)--(2.2); convergence is not inferred merely by identifying it with the
different series `sum 1/x_j`.

Suppose a positive literal odd-to-odd path `w` of weight `q` and length `L`
sends `z` to `y`, and the common future is nonperiodic. The path itself may
be unsafe. At a later odd endpoint `y_n`, measured from `y`, its total
coefficient measured from `z` is `c(w)c_n(y)`. Therefore

\[
\boxed{\mathcal Y(z)=\frac{\mathcal Y(y)}{c(w)}.}
\tag{2.4}
\]

Equivalently, concatenating corrections gives
`beta_infinity(z)=B_w/3^q+beta_infinity(y)/c(w)`. Advancing the chosen
coalescence time multiplies the numerator height and the prefix coefficient
by the same subsequent coefficient, so (2.4) is independent of that choice.
This extension of (2.3) to unsafe coalescing sources is needed whenever the
intermediate endpoint is not a renewal minimum.

Fix one nonperiodic future with a permanent-safe source, supplied by P222.
Let `C` contain all positive odd sources whose entire full shortcut future
is coefficient-safe and which eventually join this fixed future. This class
is nonempty; every one of its sources has the finite height (2.3).

Choose `x_0 in C`. Any source in the sublevel set

\[
\mathcal C_0=\{x\in\mathcal C:\mathcal Y(x)\le\mathcal Y(x_0)\}
\]

is a positive integer with `x<mathcal Y(x_0)`. Thus `C_0` is finite and
nonempty. Its least height is also the least height on all of `C`:

\[
\boxed{\text{there is }S_*\in\mathcal C\text{ minimizing }\mathcal Y.}
\tag{2.5}
\]

This is finite attainment, not well-ordering of the positive reals. It
asserts neither uniqueness nor that `S_*` is the least ordinary source.

## 3. P243: global coefficient maximality and literal bridges

First let a nonempty actual prefix `d` from `S_*` end at an odd state `y`.
Let `a` be any finite positive literal shortcut path to the same `y`; its
source may initially be even and its internal prefixes may be unsafe.
We prove

\[
\boxed{c(a)\le c(d).}
\tag{3.1}
\]

Suppose instead that `c(a)>c(d)>1`. If `a` is safe, its source `z` is odd.
For every subsequent actual prefix `u` after the common endpoint,

\[
c(au)=c(a)c(u)>c(d)c(u)=c(du)>1.
\tag{3.2}
\]

Together with the internal safety of `a`, this makes the entire future from
`z` permanent-safe. It has the same nonperiodic future and belongs to `C`.
But (2.4) gives

\[
\mathcal Y(z)=\frac{\mathcal Y(y)}{c(a)}
<\frac{\mathcal Y(y)}{c(d)}=\mathcal Y(S_*),
\]

contrary to (2.5).

If `a` is unsafe, include the empty prefix coefficient one and take the
unique minimum of all its prefix coefficients. The minimum is a number
`mu<1` at a proper positive time, because the final coefficient exceeds one.
Uniqueness follows from unique factorization. Write `a=pb` at that time.
Every nonempty prefix of `b` has coefficient greater than one, and

\[
c(b)=c(a)/\mu>c(a)>c(d).
\tag{3.3}
\]

The first bit of `b` is one: a zero would produce a still smaller prefix
coefficient. Its source `v` is therefore an actual positive odd integer.
Equation (3.2), now with `b`, places `v` in `C`, and (2.4) gives the same
contradiction. This is P87's valley mechanism with normalized-height order;
neither an ordinary-source decrease nor the least-source premise of P86 is
being assumed.

The conclusion extends to a full shortcut prefix ending at an even state.
Append its actual finite string of zero bits to the next odd endpoint.
Append the same zero string to the competitor. Both terminal coefficients
are multiplied by the same power of `1/2`, preserving a strict comparison,
and the extended target remains a prefix of the permanent-safe orbit.
Applying (3.1) at the odd endpoint proves maximality at the original
endpoint as well.

### Canonical endpoint classes give actual positive competitors

H112's finite word language uses canonical endpoint classes, so a congruence
alone must not be confused with a positive literal ancestor. The following
elementary bridge, already used in Phase 39, supplies it without X02.

For a word `w` of length `L` and weight `q>0`, let `r_2` be its unique
positive source representative modulo `2^L`, with `1<=r_2<=2^L`.
Final affine integrality forces its literal bits: modulo two the initial
bit is fixed; performing that branch leaves the same assertion for the
remaining word. Induction proves parity legality at every position, and
positivity is preserved by the positive shortcut map.

Its canonical endpoint `r_3=F_w(r_2)` satisfies

\[
1\le r_3<3^q.
\tag{3.4}
\]

Indeed, at time `i` the envelope
`n_i<=3^(q_i)2^(L-i)` propagates through both parity branches. Before any
odd step this envelope is an even integer, so its odd input is at most
the envelope minus one. The resulting bound is strict after that step and
remains strict to the endpoint, proving (3.4).

If an actual positive endpoint `M` has this same residue modulo `3^q`,
then `M=r_3+3^q t` with integer `t>=0`. Its source under `w` is exactly

\[
r_2+2^L t>0,
\tag{3.5}
\]

which follows `w` literally. Thus every canonical-class competitor used by
H112 yields a positive actual competitor at the endpoint in question.

## 4. P243: exact H112 implication without X02

A shorter same-`q` path with length deficit `k>=1` has coefficient
`2^k c(d)>c(d)`. By Section 3, every full shortcut prefix from `S_*` is
therefore shortest among **all positive literal same-`q` paths**, including
unsafe ones. Equations (3.4)--(3.5) imply, in particular, shortestness among
the safe canonical endpoint-class words in H112.

For completeness, shortestness only at odd accelerated endpoints would also
suffice for this matching. A full prefix ending between two odd endpoints
can be extended by its actual zero suffix to the next odd endpoint. This
adds no odd step and preserves a strict length improvement of a competing
path. If that competitor starts even, remove its initial zero run; the
remaining path starts at a positive odd state and is even shorter with the
same odd count. A positive literal odd-to-odd word has exact accelerated
exponents, since its next declared odd input or final odd endpoint rules
out an additional factor of two. This establishes the full-prefix versus
odd-endpoint equivalence needed below; it does not equate arbitrary formal
affine congruences with exact valuations.

The source `S_*` is one fixed positive ordinary integer realizing the entire
infinite itinerary. Once the canonical accelerated source modulus `2^E_n`
exceeds `S_*`, its positive representative is `S_*` itself. P115 therefore
gives eventual zero canonical source lifts. H112 would instead require
infinitely many nonzero lifts on this infinite safe all-prefix geodesic.
We have proved the logical implication

\[
\boxed{H112\ \Longrightarrow\ \text{there is no nonperiodic positive
integer shortcut orbit}.}
\tag{4.1}
\]

The internal inputs are P221/P222, exact affine normalization, finite
attainment, the P87 valley argument, the canonical positivity bridge, and
P115. Neither X02 nor P228/E54's finite threshold occurs in this proof.
P240 remains a separately recorded conditional historical reduction.

H112 itself is not proved. Positive nontrivial cycles are also untouched:
their repeated prefix coefficient contracts and they are not permanent-safe
nonperiodic representatives. The all-ones formal word is safe and geodesic
but represents `-1` in `Z_2`, with residues `2^n-1` and nonzero lifts; it is
not an ordinary positive-source exception. A finite zero-lift run, including
the source-167 regression, still supplies no eventual stabilization.

## 5. P244: Bellman redundancy and eventual stabilization

For a positive odd endpoint `y`, set `ell_0(y)=0`. For `q>=1`, define
`ell_q(y)` to be the minimum total exponent of a positive literal
odd-to-odd accelerated path with exactly `q` odd steps ending at `y`.
Use `ell_q(y)=+infinity` if this set is empty. For example, an odd endpoint
divisible by three has no one-step odd predecessor. Along the actual odd
orbit from a permanent-safe nonperiodic source `S`, its own prefix ensures
`ell_q(x_q)<=E_q`, so

\[
r_q=E_q-\ell_q(x_q)
\]

is always a finite nonnegative integer, with `r_0=0`.

For `q>=1`, any candidate of total exponent `L` and positive source `z`
satisfies

\[
2^Lx_q=3^qz+B>3^q,
\]

because `z>=1` and its affine correction `B` is positive. Since
`x_q=3^qY_q/2^E_q`, this is

\[
L>E_q-\log_2Y_q.
\]

Taking a shortest candidate proves

\[
\boxed{0\le r_q<\log_2Y_q<\log_2\mathcal Y(S)\qquad(q\ge1).}
\tag{5.1}
\]

The zero-step assertion needed for boundedness is simply
`r_0=0<log_2 mathcal Y(S)`, since `mathcal Y(S)>S>=1`.

A shortest path to `x_q` can be followed by its actual next step of exponent
`e_q`, yielding

\[
\ell_{q+1}(x_{q+1})\le\ell_q(x_q)+e_q.
\]

Therefore

\[
\boxed{r_{q+1}\ge r_q.}
\tag{5.2}
\]

A bounded nondecreasing integer sequence eventually becomes constant. Thus
there are integers `r>=0` and `q_0>=0` such that `r_q=r` for `q>=q_0`.
No bound on the last jump `q_0` follows from this observation. In particular,
a long observed constant run is not a certificate of eventual constancy.

The Bellman inequality concerns actual positive predecessors with exact
exponents. It does not require a probabilistic model or a finite abstraction
of the complete predecessor tree. At each fixed endpoint its finite search
can be capped by the known actual exponent `E_q`; such a finite computation
does not certify the unbounded-time stabilization assertion.

## 6. P244: finite height descent and its limits

Suppose the stabilized redundancy is `r>0`, and choose a shortest path `a`
at an index `q_0` after stabilization. Its coefficient is

\[
c(a)=2^r c(d),
\tag{6.1}
\]

where `d` is the original prefix from `S` to `x_(q_0)`. Appending the actual
future remains shortest at every later odd endpoint: its length at `x_q`
is `ell_(q_0)(x_(q_0))+E_q-E_(q_0)=E_q-r=ell_q(x_q)`.

If `a` is safe, its positive source shares the permanent-safe future by the
same coefficient comparison as (3.2), and normalized height is exactly

\[
\mathcal Y(S)/2^r.
\tag{6.2}
\]

If `a` is unsafe, cut at its unique coefficient minimum `mu<1`. Its positive
odd safe suffix has coefficient `c(a)/mu`, and its source shares the
permanent-safe future with normalized height

\[
\mu\,\mathcal Y(S)/2^r<\mathcal Y(S)/2^r.
\tag{6.3}
\]

In both cases the replacement stays in the same nonperiodic future class
and has height at most one half of the original. The proposal's universal
strictly-less-than-half sentence is not justified: (6.2) is exactly one
half when `r=1`. Neither (6.2) nor (6.3) asserts ordinary source descent.

Repeating a replacement whenever the new source has positive limiting
redundancy cannot continue infinitely. After `t` replacements its height is
at most `mathcal Y(S)/2^t`, whereas every positive source has height greater
than one. Thus

\[
2^t<\mathcal Y(S).
\tag{6.4}
\]

The final source has limiting redundancy zero, and (5.2) then forces all
its `r_q` to be zero. Its every odd prefix is a shortest positive same-`q`
path. Section 4 supplies the full shortcut and canonical-class bridges.
This recovers the geodesic conclusion of P243, but does not by itself
assert P243's stronger maximality against every different-`q` competitor.

### Effectivity boundary

The argument proves existence of a finite chain of height-decreasing
replacements. It does not provide a computable last-jump bound or a finite
test recognizing that a source is geodesic at all future times. One can
instead search for any finite witness `r_q>0` and replace immediately; each
replacement still obeys (6.2)--(6.3), so only finitely many can occur. That
procedure may keep searching forever after its final replacement. Eventual
stability of its selected source is not a certified stopping rule.

A finite algebraic half-factor control is

```text
63 --111111000--> 91,  q=6, L=9, c=729/512, safe;
31 --11111010 --> 91,  q=6, L=8, c=729/256, safe.
```

Exact enumeration at endpoint 91 with `q=6,L<=9` finds no shorter path
than length eight. These paths show the equality factor in (6.2) for a
safe one-unit shortening. They are finite controls: the actual future from
91 terminates, so they are not nonperiodic examples to which a finite
infinite-tail height is being assigned.

## 7. Shifted-correction safety obstruction

### NG43: the assertion and its exact obstruction

For a zero-prefixed tail v of length ell, write q(v) for its weight and
Rmin(v) for the least integer R>=1 for which 1^R v is safe. At the fixed
P238 vertex (ell,J), the assertion under test was:

> If v' has k>0 additional ones and 1<=k<=R-1, then safety of 1^R v implies
> safety of 1^(R-k) v'.

It looked plausible after all 10,520 Phase 39 bounded rewrites passed. The
following exact pair refutes it, without invalidating P238, which explicitly
required a separate safety check:

```text
v  = 0110110110110110001101101   q=15, Rmin=4
v' = 0011111111111111010000100   q=16, Rmin=4
ell=25, J=166692291, k=1, R=4.
```

The target d=1^4 v has (L,q,B)=(29,19,3292467211) and is safe.
The alternative a=1^3 v' has (28,19,2227364339) and is unsafe. Their actual
positive sources 358030447 and 179015223 reach the same endpoint 775093205.
Thus the shorter path is a genuine positive literal competitor, not merely
a modular or rational collision.

The unique coefficient valley of a is after its first five bits 11100,
with coefficient 27/32. Its actual state is 151044095. The remaining word

```text
11111111111111010000100
```

has length 23, weight 16, B=44046145, coefficient 43046721/8388608, and is
safe. It reaches the same endpoint and has coefficient larger than both a
and d. Its canonical source is only 49151: the actual occurrence is
49151+18*2^23, with endpoint 252227+18*3^16. These two source conventions
must not be conflated. The P243 strict-valley rescue survives this failure.

### Exhaustive finite minimality with no initial-run cutoff

For every tail prefix of length j and weight q_j, safety is precisely

\[
3^{R+q_j}>2^{R+j}.
\]

The ratio increases strictly with R, so Rmin is the maximum of the finitely
many exact integer thresholds. For fixed ordered tails v,v' with weight
gain k>0, the complete set of failing admissible initial runs is the interval

\[
\boxed{\max(Rmin(v),k+1)\le R\le Rmin(v')+k-1.}
\tag{7.1}
\]

This is an exact reduction of all R, not a choice of a search cutoff.
In particular, Rmin(v')>=2 because its first bit is zero, so nonemptiness
is equivalent to q(v)+Rmin(v)<q(v')+Rmin(v').

The generator enumerates the shifted DAG forward, starting J=1 at the
first zero; append 1 multiplies J by 3, append 0 adds 2^ell. The independent
checker enumerates each binary mask afresh and uses the positional identity

\[
J(v)=\sum_{j:v_j=0}2^j3^{\#\{i>j:v_i=1\}},
\tag{7.2}
\]

which follows by distributing D_next=3D or D+2^j. It obtains prefix weights
by a reverse scan, rather than inheriting forward threshold states.
Both implementations group the complete words by J and test (7.1).

There are 33,554,431 zero-prefixed tails in 1<=ell<=25. There are no failing
ordered pairs for ell<=24, and exactly four at ell=25, each with exactly
one failing initial run. At ell=25 there are 16,777,216 paths, 7,160,480
vertices and 13,488,484 positive-weight-gain pairs.

With ordering (ell, original-tail lexicographic, alternative-tail
lexicographic, R), the first pair is instead

```text
v  = 0110110110110010110101101
v' = 0011111111111011100001100
J=173991363; q=15,16; Rmin=4,4; k=1; R=4.
```

Its positive sources 328539247 and 164269623 coalesce at 711248276.
The supplied example is length-minimal but not lexicographically first.
The accepted minimality quantifier covers **all zero-prefixed binary tails
through length 25 and all admissible R**, not all imaginable rewrite systems,
all source sizes, or all ways of measuring a smallest counterexample.

Packed C++ arithmetic is exact with proved bounds: at length ell,
J<=3^(ell-1), inductively from max(3J,J+2^ell)<=3^ell. Hence J<=3^24<2^39;
masks use at most 24 bits. The safety threshold has R<=43 and the conservative
power bounds R+q<=68 and R+ell<127 fit checked unsigned 128-bit arithmetic.
Python independently recomputes all threshold entries with arbitrary-precision
integers. Neither implementation uses floating-point acceptance decisions.

NG43 rules out omitting the full adjusted-run safety test. It does not rule
out a source jump followed by strict-valley extraction, nor prove that a
suitable improving competitor always exists.

## 8. Alternate-predecessor clouds and weighted moments

### P245: exact positive cloud and collision-free indexing

Let x_j be the odd states of any positive ordinary non-eventually-periodic
orbit; permanent safety is not needed. Put E_j=sum_(i<j)e_i. For integers
1<=r<=floor((e_j-1)/2), define

\[
z_{j,r}=\frac{3x_j+1-4^r}{3\,4^r}.
\]

Since 4^r divides 3x_j+1 and 4^r=1 mod 3, this is an integer. Its numerator
is positive because 3x_j+1>=2^e_j>=2*4^r. Also

\[
3z_{j,r}+1=2^{e_j-2r}x_{j+1}.
\tag{8.1}
\]

The right side is even and x_(j+1) is odd. Therefore z is positive odd and
has exact valuation e_j-2r, not just divisibility by that power of two.

Let X_t be the original full shortcut orbit, X_(E_j)=x_j. For
delta_(j,r)=E_j+2r, direct intermediate even-state calculation gives
X_delta=3z+1, hence T(z)=X_(delta+1). In particular the new orbit has joined
the old orbit after one shortcut step, with phase offset delta; it reaches
the next odd endpoint after e_j-2r steps. All offsets are distinct because
they lie strictly inside the disjoint intervals (E_j,E_(j+1)).

If T^t(z_(j,r))=T^t(z_(j',r')) for distinct pairs, advance until t>=1.
Then X_(t+delta)=X_(t+delta'), a repeated state at different times in the
original deterministic orbit. That forces eventual periodicity, contrary to
the hypothesis. Thus the indexed cloud is injective, and its set is
equal-time collision-free, as required by P220/P221.

The nonperiodicity hypothesis cannot be omitted. The ordinary source 21 has
e=6 and cloud {5,1}. Both cloud points have T^4 equal to 1 (they already
coincide at time 3). Local algebra remains valid, but the future is periodic.
The finite audit records this control explicitly and never treats sampled
terminating orbits as infinite nonperiodic evidence.

### P246: the moment and its direct dependency

For each real p>rho_star, choose rho strictly between rho_star and p.
P221 applied to the cloud gives sum_(j,r) z_(j,r)^(-p)<infinity. Since
z_(j,r)<(x_j+1)/4^r, this implies the requested double sum.

A simpler argument gives a stronger statement over **all** j:

\[
\frac{2^{e_j}}{x_j+1}
=\frac{3x_j+1}{(x_j+1)x_{j+1}}<\frac3{x_{j+1}},
\qquad
\boxed{\sum_j\left(\frac{2^{e_j}}{x_j+1}\right)^p<\infty.}
\tag{8.2}
\]

Here P221 applies directly to the distinct odd orbit, with the same choice
rho_star<rho<p. No cloud, permanent safety, X02, or new external theorem is
needed for this conclusion. For R=floor((e-1)/2), the elementary geometric
sum obeys

\[
\sum_{r=1}^R4^{pr}\le\frac{2^p}{4^p-1}2^{pe},
\]

so (8.2) also implies the full double-sum formulation. Since rho_star<1,
p=1 is allowed and in particular sum_(j:e_j>=3)2^e_j/(x_j+1)<infinity.
Equivalently, its summand tends to zero, which is already forced by
x_(j+1)->infinity. The moment is therefore a direct transition/sparsity
corollary, not a separate obstruction to an infinite permanent-safe orbit.
The cloud's indexed collision-free structure is recorded separately as P245.

If one selects the least positive source of a nonconvergent future class,
every z in the cloud is another positive nonconvergent source and hence at
least that minimum. This ordinary-source comparison is logically separate
from both collision-free sparsity and normalized-height minimization.

## 9. Independent finite verification and reproducibility

The experiment contract is
[`phase40-normalized-height-bellman.json`](../../experiments/phase40-normalized-height-bellman.json).
It was recorded before the acceptance computations. The four generated
artifacts contain 1,024 Bellman rows (odd sources 1..255, eight odd steps),
448 finite normalization split identities, the complete tail-level counts
and witnesses above, 65,536 direct transitions, 12,954 alternate-predecessor
rows (odd sources 1..4095, 32 odd steps), and retained adversarial controls.
Bellman rows test finite identities even on periodic sources; the infinite
convergence theorem is established in Sections 2--6, not by sampling.

The generator uses backward Dijkstra search for shortest total exponent.
The independent verifier uses exact-total-length inverse feasibility,
increasing candidate lengths from q to the actual E. Positivity and oddness
are reconstructed at every inverse step. It rebuilds finite normalization
from direct products, affine B from positional sums, and source cylinders
by parity lifting; it imports no Phase 40 search implementation. Mathematical
proofs were independently audited in parallel; separate files or agents alone
are not treated as proof of logical independence.

The retained controls include all six mandatory families, both cited NG43
witnesses, NG22's formal companion, NG24's failed prefix congruence, NG41's
scalar survivor, NG42's orientation, source 167's eleven zero lifts before
coefficient crossing, the positive periodic cloud control, and negative cycles.
These are finite and scoped controls, not newly established infinite examples.

Commands, actual test results, input hashes, and the acceptance audit are in
[`PHASE40_RUN_RESULTS.md`](../../../PHASE40_RUN_RESULTS.md). The SHA-256
manifest covers generated evidence, while the Git commit records the code
and mathematical proof. This phase introduces no new external input or
literature-wide novelty claim.

## What this result does not prove

The logical reduction does not prove H112, force a nonzero lift, or exclude
one positive permanent-safe source without an additional theorem. Finite
Bellman checks do not recognize eventual stabilization. Normalized-height
descent is not a universal ordinary-source descent rule. Nontrivial positive
cycles and their arbitrary-area exclusion remain separate. No statement
here proves the Collatz conjecture. `proves_collatz=false`.
