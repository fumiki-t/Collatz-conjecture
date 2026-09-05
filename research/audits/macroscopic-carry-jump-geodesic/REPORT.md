# Phase 39 independent audit: macroscopic carry and jump geodesics

**Audit date:** 2026-09-04

**Base commit:** `cb31e7960c1fa593d3b96b4259ae22d513a3d13e`

**Collatz status:** `OPEN`

**`proves_collatz=false`**

The supplied Phase 39 note is a research proposal, not an authority for its
own claims. The audit accepts the results below with explicit carry domains,
an identity exception, a restricted interpretation of finite dictionaries,
full-word safety in the jump graph, and positive ordinary integrality in the
cycle-direction theorem. The conditional H112 reduction includes the initial
odd source in its reciprocal sum and supplies the positive-endpoint argument
needed to pass from an endpoint cylinder to a literal ancestor.

## 1. Classification and conventions

| ID | Status | Audited result |
|---|---|---|
| P235 | `VERIFIED_THEOREM` | Current-state form of the nonnegative-index P91 prefix carry. |
| P236 | `VERIFIED_THEOREM` | Every fixed distinct local relation eventually fails the direct prefix-carry test on a P222 orbit. |
| P237 | `VERIFIED_THEOREM` | Exact correction bound and macroscopic length deficit for nonzero carries. |
| P238 | `VERIFIED_THEOREM` | Universal safe jump family, shifted-correction tail graph, and safe-source maximality. |
| P239 | `VERIFIED_THEOREM` | Renewal-boundary occupancy is strictly below `2X^(29/30)`. |
| P240 | `CONDITIONAL` | X02 and H112, together with P222/P228/E54, exclude the nonperiodic branch. |
| P241 | `VERIFIED_THEOREM` | Positive integer cycle event directions and the event-count lower bound. |
| E55 | `VERIFIED_FINITE` | Bounded carry, graph, capacity, endpoint-lift, cycle and adversarial reconstruction. |
| H112, H72, H133 | `OPEN` | Infinite ordinary geodesics, permanent-safe tails and remaining positive cycles are not excluded. |

The full shortcut map throughout is

\[
T(x)=\begin{cases}x/2,&x\equiv0\pmod2,\\
(3x+1)/2,&x\equiv1\pmod2.\end{cases}
\]

A chronological binary word `w` has length `L`, odd count `q`, and affine map

\[
F_w(x)=\frac{3^q x+B(w)}{2^L},\qquad c(w)=\frac{3^q}{2^L}.
\]

It is coefficient-safe if every nonempty prefix `v` satisfies
`3^Q(v)>2^L(v)`. Positive-length equality is impossible by unique
factorization. An actual occurrence additionally means that its bits are the
literal parities of the stated integer trajectory. Affine maps on arbitrary
real inputs are not automatically actual occurrences.

An accelerated odd step is `x_(j+1)=(3x_j+1)/2^e_j`, with `e_j>=1` equal to
the exact two-adic valuation for a positive odd integer orbit. Its full
shortcut word is `1` followed by `e_j-1` zeros. Ordinary state, companion,
and shifted correction are different quantities.

## 2. P235: current-state prefix carry

Take fixed words `a,d` satisfying

\[
q_d=q_a+s,\qquad L_d=L_a+k,\qquad k,s\in\mathbb Z_{\ge0},
\]

and suppose the local carry

\[
m=\frac{2^kB(a)-B(d)}{3^{q_a}}
\]

is an integer. Clearing denominators proves

\[
F_d(y)=F_a(x)\quad\Longleftrightarrow\quad
3^s y=2^k x+m.
\tag{2.1}
\]

Let a common chronological prefix `p` have odd count `Q`, length `L`, and
an actual occurrence sending `N` to `S`. Thus

\[
B(p)=2^LS-3^QN.
\]

Put `alpha=2^k-3^s`. Exact affine composition makes the prefixed carry

\[
M=\frac{\alpha B(p)+2^Lm}{3^Q}
 =\frac{2^L(\alpha S+m)}{3^Q}-\alpha N.
\]

Because `2^L` is a unit modulo `3^Q`,

\[
\boxed{M\in\mathbb Z\quad\Longleftrightarrow\quad
3^Q\mid(2^k-3^s)S+m.}
\tag{2.2}
\]

This includes the empty prefix, where `Q=L=0`. It is precisely the affine
carry condition, not a proof of an integer positive ancestor, literal
legality, descent or safety.

The stated theorem deliberately assumes `k,s>=0` and integral `m`. General
cross-Q ancestors can have `s<0`, as the earlier frontier work already shows.
Such a relation requires an explicitly denominator-cleared formulation;
it is not silently included in (2.2). Nor does this theorem cover a
negative-length deficit by treating powers of two as ordinary integers.

## 3. P236: fixed distinct relations eventually fail

Consider a positive nonperiodic permanent-safe orbit as in P222, beginning
at odd source `S_0`. Write its accelerated odd states as `S(Q)`, and its
total shortcut length through `Q` accelerated steps as `E_Q`. The exact
normalization and companion product give

\[
Y_Q=S_0\prod_{j<Q}\left(1+\frac1{3S(j)}\right)
       =S_0+\frac{B_Q}{3^Q},\qquad
Y_Q<S_0+h_0=:C.
\]

Since `E_Q>=Q`,

\[
\boxed{S(Q)=\frac{3^Q}{2^{E_Q}}Y_Q<C(3/2)^Q.}
\tag{3.1}
\]

For a fixed P235 relation,

\[
\frac{|\alpha S(Q)+m|}{3^Q}
 <\frac{|\alpha|C}{2^Q}+\frac{|m|}{3^Q}\longrightarrow0.
\tag{3.2}
\]

A nonperiodic deterministic positive orbit has distinct integer states, so
`S(Q)->infinity`. If `alpha!=0`, its fixed affine expression
`alpha S(Q)+m` is eventually nonzero; if `alpha=0,m!=0`, it is a nonzero
constant. Consequently (2.2) fails for all sufficiently large `Q` unless
`alpha=m=0`.

Under P235's nonnegative-index conventions, `2^k=3^s` forces `k=s=0`.
If also `m=0`, the words have equal length, odd count and correction. These
data determine the length-`L` parity cylinder, hence the literal word, so
`a=d`. Therefore every fixed relation between distinct words has only
finitely many direct prefix-carry depths on this orbit.

### Exact-zero and identity boundaries

The identity `a=d=1`, `k=s=m=0` has zero numerator at every depth. It must
be excluded from the distinct-relation statement.

At an actual legal occurrence of `d`, zero numerator gives
`F_a(S)=F_d(S)`. An integral affine endpoint from an integer source implies
literal legality: reducing the first affine numerator modulo two recovers
the first required parity, and induction recovers all remaining bits.
Thus both words are legal from `S`. Equal lengths force identical words;
different lengths force a repeated state and hence an eventually periodic
orbit. This independently audits the proposal's deterministic argument.

The positive periodic exception is exact:

```text
a=1, d=101, S=1, k=2, s=1, m=-1;
F_a(1)=F_d(1)=2, and (4-3)*1-1=0.
```

Negative cycles also lie outside the positive nonperiodic theorem. For
example `a=1,d=11,S=-1,k=s=1,m=-1` has zero numerator and both endpoints
equal to `-1`.

Taking the maximum of finitely many eventual cutoffs excludes arbitrarily
deep direct common-prefix lifts from a fixed finite dictionary. The broader
sentence that no finite dictionary can prove H72 is not accepted. A finite
dictionary might generate increasingly large composite relations or be used
in a different argument; neither possibility is excluded by (3.2).

## 4. P237: a nonzero successful carry is macroscopic

Let `a,d` be safe words in P235's domain, and assume coefficient dominance
`2^k>=3^s`, equivalently `c(a)>=c(d)`. P97's exact odd-position expansion is

\[
\frac{B(w)}{3^q}=\sum_{j=0}^{q-1}\frac{2^{d_j}}{3^{j+1}}.
\]

The first term is `1/3`, and safety makes each later term strictly below
`1/3`. Thus `B/3^q<=q/3`, with equality at `q=1`; the empty word has
`q=B=0`. The triangle inequality gives the valid weak bound

\[
|m|\le\frac{2^kq_a+3^sq_d}{3}
       \le\frac{2^k(q_a+q_d)}3.
\tag{4.1}
\]

For a nonzero numerator passing (2.2),

\[
3^Q\le|(2^k-3^s)S(Q)+m|
 \le 2^k\left(S(Q)+\frac{q_a+q_d}{3}\right).
\tag{4.2}
\]

This is the exact certificate form; logarithms merely rewrite it as

\[
\boxed{k\ge Q\log_2 3-
\log_2\left(S(Q)+(q_a+q_d)/3\right).}
\tag{4.3}
\]

For a sequence of such local relations at increasing depths of one fixed
orbit, suppose `q_a+q_d=exp(o(Q))`. It is then `o((3/2)^Q)`, so (3.1)
and (4.3) give

\[
\boxed{k\ge Q-O(1),}
\tag{4.4}
\]

where the constant may depend on that orbit and on when the stated
subexponential bound takes effect. This implies the proposed weaker
`k>=Q-o(Q)`. Neither version is an effective uniform last-rewrite bound or
an ancestor construction. A zero carry and a relation outside P235's domain
cannot be accepted by appealing to (4.2).

## 5. P238: the universal jump and exact tail graph

For `r>=4`, set `d_r=1^r00` and `a_r=1^(r-1)01`. The correction recurrence
gives

\[
B(d_r)=3^r-2^r,\qquad B(a_r)=3^r-2^{r-1},
\]

and therefore

\[
\boxed{F_{d_r}(2x+1)=F_{a_r}(x).}
\tag{5.1}
\]

The all-one prefixes are safe. For `d_r`, it therefore suffices to check
the final coefficient `3^r/2^(r+2)`; it is above one at `r=4` and increases
with `r`. For `a_r`, it suffices to check the
first-zero prefix `3^(r-1)/2^r>1`; the final odd step increases it. Thus
both words are safe for every `r>=4`. At `r=3`, `d_r` ends with coefficient
`27/32`, so the simultaneous-safety cutoff cannot be reduced.

The least member gives the literal positive downward rewrite

```text
11101 from 7:   7,11,17,26,13,20
111100 from15: 15,23,35,53,80,40,20.
```

Here `k=1,s=0,m=1`, so P235's current-state carry is exactly
`3^Q | S+1`. Common right suffixes preserve (5.1) and coefficient dominance;
the extended target still has to be safe to use P86. An arbitrary suffix
does not automatically preserve coefficient safety.

### Shifted correction and collision coordinates

Define

\[
D(w)=B(w)+2^{L(w)}-3^{Q(w)}.
\]

Directly appending a bit gives

\[
D(w1)=3D(w),\qquad D(w0)=D(w)+2^{L(w)}.
\tag{5.2}
\]

If `w=1^R0v`, the tail length `ell` includes the first zero. Initially
`ell=1`, `D(1^R0)=2^R`, and `J_1=1`. The remaining tail bits follow

\[
J_{\ell+1}=\begin{cases}
3J_\ell,&\text{next bit is }1,\\
J_\ell+2^\ell,&\text{next bit is }0.
\end{cases}
\tag{5.3}
\]

Every `J` is odd. At a fixed vertex `(ell,J)`, suppose `v'` has `k` more
ones than `v`. For `w'=1^(R-k)0v'`,

\[
Q(w')=Q(w),\quad L(w')=L(w)-k,\quad D(w)=2^kD(w').
\]

The shifted affine identity

\[
F_w(z)+1=\frac{3^{Q(w)}(z+1)+D(w)}{2^{L(w)}}
\]

then proves

\[
\boxed{F_w(S)=F_{w'}\left((S+1)/2^k-1\right).}
\tag{5.4}
\]

The first collision is `J_2=3`: appending either zero or one to `J_1=1`
gives the same vertex with weights zero and one. It recovers (5.1).

### Positive ordinary sources and safe maximality

Suppose `w` is an actual prefix from positive integer `S`, with maximal
initial one-run `R` followed by zero. Iterating its first `R` odd branches
gives

\[
T^R(S)=3^R(S+1)/2^R-1.
\]

The next state is even, so `(S+1)/2^R` is odd and
`v2(S+1)=R`. If `1<=k<=R-1`, the alternate source
`x=(S+1)/2^k-1` is consequently a positive odd integer with `x<S`.
Equation (5.4) makes its endpoint integral, hence the alternate word is
literal by the parity argument in Section 3. Its coefficient is
`c(w')=2^kc(w)`.

Safety remains a separate condition. For a tail prefix of length `j`,
including its initial zero, let `t_j` count its ones. The exact test is

\[
3^{R+t_j}>2^{R+j}\qquad\text{for every }j.
\tag{5.5}
\]

For the alternate path, this test must use its own run `R-k` and its own
prefix weights. For the least positive permanent-safe discrepancy-escaping
nonperiodic source, P86 now forbids every such positive safe alternative.
Each prefix containing a zero is therefore maximal in tail-one count
among safe paths to its vertex that fit the available run budget.

This is not an assertion that an unrestricted maximum-weight path is safe.
At fixed `(ell,J)`, a fixed weight determines the literal tail uniquely:
it determines `Q,L,D`, hence `B`, hence the parity cylinder. This useful
coordinate fact still supplies no global confluence or extinction theorem.

## 6. P239: capacity of the renewal-boundary subset

Let `S_i` be the renewal-boundary states of a P222 orbit. They are distinct
odd positive integers, and every nonempty future prefix from each of them
has coefficient strictly above one. Let `X>=1` be an integer interval length
and consider any translated half-open interval `[a,a+X)`.

When `X=1`, occupancy is at most one, hence below `2X^(29/30)`.
For `X>=2`, put `N=ceil(log_2 X)`. A length-`N` parity vector specifies
one residue modulo `2^N`, so distinct integer sources in this interval have
distinct vectors. Their first bit is one, and their total weight satisfies
`3^s>2^N`. Consequently occupancy is at most

\[
C_N=\sum_{\substack{1\le s\le N\\3^s>2^N}}
\binom{N-1}{s-1}.
\tag{6.1}
\]

Here the first-bit restriction is retained exactly. To prove an all-scale
bound, it is enough to majorize this by the corresponding unrestricted
high-weight binomial tail. Set `p=14/23`. The exact comparisons

\[
3^{14}<2^{23},\qquad
23^{690}<2^{667}14^{420}9^{270}
\tag{6.2}
\]

give `1/2<p<1/log_2 3` and `H_2(p)<29/30`, respectively. For every term
in the high-weight tail, `s>pN`. Since `p>1/2`,

\[
p^s(1-p)^{N-s}>p^{pN}(1-p)^{(1-p)N}=2^{-NH_2(p)}.
\]

Summing these terms inside `(p+(1-p))^N=1` gives

\[
C_N<2^{NH_2(p)}<2^{29N/30}.
\]

Finally `2^N<2X` and `29/30<1`, so

\[
\boxed{\#\{S_i\in[a,a+X)\}<2X^{29/30}.}
\tag{6.3}
\]

The constant improves P220's general `32` for this subset; its exponent
does not improve. The binomial rows through `N=500` are finite checks of
(6.1), not an input to the all-`N` entropy argument. The theorem concerns
one actual renewal-boundary set, not canonical-address multiplicity.

## 7. P240: the conditional reduction to H112

Assume a positive nonperiodic orbit exists. By P222 there is a nonempty set
of positive ordinary sources with permanent coefficient safety,
discrepancy tending to infinity, and nonperiodic future. Choose its least
element `S`. This is least in that precise class; the argument does not
assume that every smaller positive integer is already known to converge.

Under X02, every such source is at least
`V=2075*2^60>2^49`. The weak inequality `S>=V` suffices, independently of
the endpoint convention in the external verification range. Every later
state on this safe orbit is strictly greater than `S`.

The set of all odd states `x_0=S,x_1,...` is equal-time collision-free. Its
occupancy in the shell `[2^N,2^(N+1))` is bounded by P228's `O_N`.
P228/E54 and the analytic tail certificate from Phase 38 prove

\[
\sum_{j\ge0}\frac1{x_j}
\le\sum_{N\ge49}\frac{O_N}{2^N}
<\frac{2079}{1000}<\frac{842}{405}<3\log2.
\tag{7.1}
\]

The initial source is included. Therefore

\[
\log(Y_\infty/S)
=\sum_{j\ge0}\log\left(1+\frac1{3x_j}\right)
<\frac13\sum_{j\ge0}\frac1{x_j}<\log2,
\]

and

\[
\boxed{Y_\infty<2S.}
\tag{7.2}
\]

### Positive endpoint-cylinder bridge

For any binary word of length `L` with `q>=1`, let `r_2` be its least
positive source residue modulo `2^L`, and let `r_3=F_w(r_2)`. The literal
trace is positive. Its integer state after `j` bits satisfies

\[
n_j\le3^{q_j}2^{L-j},
\]

and the inequality becomes strict after its first odd bit. Indeed, before
that bit only exact halving occurs; the odd integer at that bit is at most
the integer envelope minus one, and `(3n+1)/2` then lies strictly below the
next envelope. Strictness propagates through both branches. At the endpoint,

\[
1\le r_2\le2^L,\qquad 1\le r_3<3^q.
\tag{7.3}
\]

Every positive integer endpoint `M` in the residue class `r_3 mod 3^q`
is `M=r_3+t3^q` for an integer `t>=0`. Its source is
`r_2+t2^L>0`, and the word is literal there. Thus an endpoint-cylinder
competitor at a positive endpoint really supplies a positive ordinary
ancestor. No negative canonical lift is being promoted to such an ancestor.

### All-prefix geodesicity and the remaining hypothesis

Let a safe prefix `d` from `S` reach `M` with `j` odd bits. Suppose a safe
same-`j` word `a`, shorter by `k>=1`, reaches the same endpoint. If stated
as an endpoint-cylinder condition, (7.3) supplies its positive source `x`.
Equating affine maps gives

\[
Y_j=S+B(d)/3^j
=2^k\left(x+B(a)/3^j\right).
\]

Because `B(a)>0`,

\[
0<x<Y_j/2^k<Y_\infty/2<S.
\]

Also `c(a)=2^kc(d)`. P86's surplus-dominating ancestor argument applies:
before the common endpoint `a` is safe, and afterward its larger accumulated
coefficient preserves the original safe future and discrepancy escape.
Its future is the same nonperiodic future. This contradicts the choice of
`S`. Hence every prefix of this least source is same-Q geodesic.

P115 makes the canonical accelerated residues of a fixed positive ordinary
source eventually constant, with eventually zero lifts. H112 asserts that
an infinite coefficient-safe all-prefix same-Q-geodesic branch instead has
infinitely many nonzero lifts. If H112 is supplied, the two conclusions
contradict each other. Thus

\[
\boxed{\text{P222 + P228/E54 + X02 + H112 exclude nonperiodic
positive orbits}.}
\tag{7.4}
\]

X02 remains `EXTERNAL_EVIDENCE`, and H112 remains `OPEN`; P240 is
`CONDITIONAL`. A weaker sufficient external premise is that no source in
the chosen permanent-safe nonperiodic class lies below `2^49`. No internal
finite exhaustion of that range is supplied here. Critical cycles are not
covered by (7.4).

## 8. P241: positive-cycle event geometry

Let `x_j` be positive odd integer cycle states with exact exponents `e_j`,
and put `y_j=(x_j+1)/2`. The shifted recurrence is

\[
2^{e_j}y_{j+1}=3y_j+(2^{e_j-1}-1).
\tag{8.1}
\]

If `e_j=1`, then `y_(j+1)=3y_j/2>y_j`. If `e_j>=2`, then

\[
2^{e_j}(y_{j+1}-y_j)
=(2^{e_j-1}-1)-(2^{e_j}-3)y_j.
\]

Here `y_j>=1` is essential. The right side is at most
`2-2^(e_j-1)`, and equality at zero is possible only for `e_j=2,y_j=1`.
Thus every event `e_j>=2` in a nontrivial positive integer cycle is a strict
descent, while each `e_j=1` step is a strict ascent. The trivial cycle
`x=1,e=2` gives the unique equality case.

The integer hypothesis cannot be dropped: the positive rational fixed
cycle `x=1/5,e=3` has `y=3/5` and equality. Negative cycles are outside the
direction statement as well.

Let `q` be the odd period, `L=sum e_j`, `lambda=3^q/2^L`,
`m=min x_j>0`, and `M=# {j:e_j>=2}`. Multiplying (8.1) around the cycle
gives

\[
\frac1\lambda=
\prod_{j:e_j\ge2}\left(1+
\frac{2^{e_j-1}-1}{3y_j}\right).
\tag{8.2}
\]

Since `y_(j+1)>=(m+1)/2`,

\[
3y_j\ge2^{e_j-1}m+1,
\qquad
0<\frac{2^{e_j-1}-1}{3y_j}<\frac1m
\quad(e_j\ge2).
\]

There must be at least one event: all `e_j=1` would be strict ascents around
a finite cycle. The strict inequality `log(1+u)<u` therefore proves

\[
\boxed{M>m\log(1/\lambda).}
\tag{8.3}
\]

For a noncritical cycle `lambda<1/2`, it follows that `M>m log2`.
Unlike the direction theorem, the event-product bound remains valid for
positive rational formal cycles with `m>0` and exponents `e_j>=1`.
Neither bound excludes the finite minimum range left by P229 or supplies
an arbitrary-area critical-cycle exclusion.

## 9. E55: finite reconstruction and independent verification

The finite audit has declared cutoffs. It does not use the absence of a
counterexample in these cutoffs to prove Sections 2--8.

| Component | Exact finite scope |
|---|---|
| Local carry | All 51 safe words of length at most 8; 172 distinct nonnegative-index integral-carry relations; all 127 prefixes of length at most 6 including the empty word; 21,844 relation-prefix rows. |
| Carry diagnostics | 6,391 passing carry tests, 93 positive safe downward occurrences, and 570 nonzero dominant-carry bound checks. |
| Universal family | Literal reconstruction for `4<=r<=32`, accompanying the all-`r` symbolic proof. |
| Tail graph | Every tail through length 12 and every initial run `1<=R<=12`; 4,095 tail paths in total and 10,520 candidate jump pairs. |
| Tail safety | Every candidate is tested for full-word safety; all 10,520 pass in this finite range, with maximum observed gain 3. |
| Boundary capacity | All 500 exact `C_N` rows for `1<=N<=500` and the integer comparisons in (6.2). |
| Positive endpoints | All 8,178 words of length at most 12 containing an odd bit; 24,534 lifted-source checks with lift parameters 0, 1 and 3. |
| Rational cycles | Exponent words with `1<=q<=5`, `1<=e_j<=4`; 1,320 positive rational cycle rows, including repeated or nonprimitive words. |
| Actual events | Every odd source from 1 through 1,023 for 64 accelerated steps; 32,768 event checks. |

The carry artifact also records rational envelope cutoffs for the illustrative
assumption C=100 in (3.1). These are conditional arithmetic diagnostics, not
an assertion that a nonperiodic orbit with that bound exists. Tail length ell
counts the first zero: ell<=12 means the residual suffix v has length <=11.

The finite graph does not prove that maximum-weight candidates stay safe at
larger depths, that gain three is a global ceiling, or that the graph is
confluent. Rational cycle rows are formal exact checks, not positive integer
cycle evidence. Repeated trivial cycle words are not counted as new primitive
cycles. Actual finite event traces are not assumed to be nonperiodic.

The evidence is generated by
[`src/phase39_search.py`](../../../src/phase39_search.py) and reconstructed
by [`verifier/verify_phase39.py`](../../../verifier/verify_phase39.py).
The verifier must not import the search implementation and must recompute
derived arithmetic and finite row digests. Acceptance additionally requires
tamper rejection tests, the recorded test results, and the SHA-256 manifest;
the exact commands and acceptance commit are recorded in
[`PHASE39_RUN_RESULTS.md`](../../../PHASE39_RUN_RESULTS.md) and the
experiment manifest.

## 10. Preserved falsifiers and external-dependency boundary

The regression corpus retains `2^m-1`, `8^m-5`, `(110|111)^*`,
`A=11101`, `B=1100`, and `A^rB^s`. In particular,
`111011100` retains the exact map `(729x+817)/512` and fixed point
`-817/217`. It also retains the NG22 formal companion policy, NG24's
left-prefix endpoint mismatch, the NG41 scalar-survivor record, NG42's
orientation distinction, source 167, the trivial cycle and negative cycles.

The repaired identity, periodic and rational-direction omissions are explicit
boundary examples, not grounds to erase earlier failed approaches or recycle
their IDs. A real/2-adic transfer with different completion limits remains
compatible; this phase supplies no contradiction between completions.

No new external mathematical theorem is invoked. P235--P239 and P241 use
the repository's stated exact identities and elementary arguments. P240
uses X02 only with its existing `EXTERNAL_EVIDENCE` status and takes H112
as an unproved premise. No literature-wide novelty claim is made for the
affine normalization, entropy estimate or cycle product argument.

## What this result does not prove

- H112, H72, P80, or the nonexistence of a positive ordinary infinite safe
  geodesic without the stated conditional inputs.
- That every safe source has a macroscopic ancestor, or that finitely many
  graph collisions give a recursive all-depth rejection rule.
- That all signed cross-Q rewrites satisfy the nonnegative-index theorem
  without clearing and checking their denominators.
- That fixed direct rewrite dictionaries cannot participate in any possible
  proof method or generate unbounded composite relations.
- An internal exhaustion below `2^49`, unconditional removal of noncritical
  cycles, or an arbitrary-area critical-cycle exclusion.
- Pointwise defect control at every odd iterate from control only at renewal
  boundaries, or address anti-concentration from a one-orbit occupancy bound.
- The Collatz conjecture.

`proves_collatz=false`.
