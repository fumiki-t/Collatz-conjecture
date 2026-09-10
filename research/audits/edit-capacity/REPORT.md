# Phase 44 audit — zero-edit capacity and oscillating defect

Date: 2026-09-10. Base: `44430b21705bd69acb6cc29760ee27bdf2433b1f`.
Branch: `feat/phase44-edit-capacity`. `proves_collatz=false`.
The [supplied proposal](PROPOSAL.md) used a Phase 42 base; this audit preserves
the already accepted Phase 43 normalization barriers, including both NG46
controls. The proposal, its scripts, and its own verdicts are not authorities.

## 1. Classification and independent changes

| Claim | Status | Scope |
|---|---|---|
| P262 | `VERIFIED_THEOREM` | Finite zero-edit capacity for positive literal distinct input states, all edit budgets. |
| P263 | `VERIFIED_THEOREM` | Fixed-edit downward-variation hierarchy, without monotone defect. |
| P264 | `VERIFIED_THEOREM` | Logarithmic-height positive variation density; sublinear variation forces superlogarithmic maximum defect. |
| P265 | `VERIFIED_THEOREM` | Specified oscillating formal model, its asymptotics, all-depth pure-CAP vacuity, and real/2-adic properties. |
| P266 | `VERIFIED_THEOREM` | No positive ordinary source for that model or its finite extension; the extension retains all-depth same-vertex no-gain. |
| P267 | `VERIFIED_THEOREM` | Separate finite distinct-trajectory version of internal interval sparsity. |
| E60 | `VERIFIED_FINITE` | Million-step model, eight repeat-and-split certificates and the explicitly bounded audits below. |

All proofs below were checked before running supplied code; supplied code was
read but **not executed or adopted as a verifier**. The repository generator
uses the published recurrence. Its checker instead jumps to height-change
events by binary search within constant-target epochs; it obtains logarithms
from `log_2(3)=3/2+log(9/8)/(2 log 2)`. Sliding integer windows are checked by
range additions and literal byte factors. Small edit balls are reconstructed
by inverse zero-only edit-distance DP, not the generator's deletion/insertion
enumeration. Every accepting check uses explicit exceptions, including under
`python -O`. Independent code does not replace the written universal proof.

Dependencies: P125 parity separation, P252's elementary infinite mechanical
factor bound, and P221 only for the *general infinite-orbit* corollaries.
The specified model's exclusion proves its own finite normalization and does
not use P221, X02, external density theorems, or monotone-defect P254.
P267 uses P219 and rederives the induction constants of P220, not a direct
application of P220 to a converging orbit. No new external theorem or
literature-wide novelty is asserted.

## 2. P262: conventions and zero-edit capacity

Use shortcut input parity: T(x)=x/2 for even x, (3x+1)/2 for odd x.
Let S be a positive odd integer. For q complete odd blocks put

```text
x_0=S, e_j=v_2(3x_j+1)>=1, x_(j+1)=(3x_j+1)/2^e_j,
alpha=log_2 3, E_j=sum_(t<j)e_t, f_j=floor(j alpha), b_j=f_(j+1)-f_j,
a_j=f_j-E_j, H=max_(0<=j<=q)a_j, D=sum_(j<q)(a_j-a_(j+1))_+,
W=product_(j<q) 1 0^(e_j-1), L=E_q.
```

Here D means downward variation, not a cycle denominator. q=0 is permitted.
Assume the **L input states** T^i(S), 0<=i<L, are distinct; the closing
endpoint may repeat. No finite safety, a_j>=0, or coefficient maximality is
assumed. H>=0 because a_0=0. Set

```text
Y_j=2^E_j x_j/3^j = S+sum_(t<j) 2^E_t/3^(t+1).
```

Choose any integer K with 2^K>=3Y_q; positivity implies K>=2. Put n=H+K.
At odd inputs the coefficient is `3^j/2^E_j=2^(a_j+theta_j)<2^(H+1)`.
An odd step multiplies it by 3/2 and the following even steps decrease it.
The normalized value at every input is at most Y_q. Hence every counted
state satisfies `0<T^i(S)<3*2^H Y_q<=2^n`. P125 (one-step differences divide
by two and multiply by an odd number) implies distinct positive states in
this range have distinct length-n parity windows. There are
`M=max(L-n+1,0)` such windows entirely in W. Future beyond W is not needed.

### 2.1 Alignment and charging, including boundary cases

The infinite mechanical baseline sigma has ones at f_j and gaps b_j in
{1,2}. W is aligned to its first q blocks by preserving the ordered ones
and the available original zeros; only **zeros** may be inserted/deleted.
Since `a_(j+1)-a_j=b_j-e_j<=1`, every upward change deletes one zero,
and a downward change of magnitude d inserts d zeros. Thus

```text
U-D=a_q, t=U+D=a_q+2D>=0.
```

Charge an inserted zero when it lies inside a window. Charge a deleted zero
at its resulting gap g only for windows [i,i+n) with **i<g<i+n**. Deletions
at either endpoint are not charged. Multiple deletions at one gap are
counted with multiplicity. Insertions belong to at most n windows and
deleted gaps to at most n-1; consequently `sum_i r_i<=nt`.

To exhibit the factor behind a window, take the baseline substring from its
first retained character to its last retained character, inclusive. Delete
the intervening deleted zeros and insert the window's extra zeros. Its total
edit cost is no greater than the charged r_i; exterior charged gaps may be
ignored. If no retained character exists, use the empty factor and insert
all n zeros. This proves the alignment assertion for windows wholly inside
inserted runs, windows spanning deletions, arbitrary insertion runs, and
truncated boundary blocks. It is not an arbitrary-bit edit model.

### 2.2 Ball count

Sigma has at most m+1 length-m factors, with one empty factor. Indeed
`sigma_t=ceil((t+1)/alpha)-ceil(t/alpha)`: the rotation partition has at most
m+1 arcs, and its ceiling boundary values agree with adjacent arcs. This is
the infinite-word fact; NG32's terminal-mutated finite word is not included.

To obtain a length-n word from a length-m factor with a deletions and b
insertions, m=n+a-b. Overcount the deletion positions among *all* m
positions, then choose the b zero insertion positions among n output
positions. The count is at most `(m+1) binom(m,a) binom(n,b)`; there is no
factor 2^b. Terms with invalid m or b vanish. For j=a+b, m<=n+j, and allowing
additional invalid terms can only increase an upper bound. Vandermonde and
hockey-stick give, for every integer r>=0,

```text
B(n,r) <= (n+r+1) sum_(j=0)^r sum_(a+b=j) binom(n+j,a) binom(n,b)
        = (n+r+1) sum_(j=0)^r binom(2n+j,j)
        = (n+r+1) binom(2n+r+1,r).
```

The number of windows charged at least r+1 is at most floor(nt/(r+1)).
All other windows have distinct words, so for **all r>=0 simultaneously**,

```text
max(E_q-n+1,0) <= (n+r+1) binom(2n+r+1,r) + floor(n(a_q+2D)/(r+1)). (EDIT-CAP)
```

No assumption r<n is used. If there are no windows the inequality is
trivial. If n=1 in the abstract edit lemma there are no internal gaps; the
literal positive-orbit application itself always has n>=2.

## 3. P263 and P264: infinite variation costs

Let a positive ordinary orbit be permanent coefficient-safe. A positive
cycle has multiplier below one, so repetition would eventually violate
safety. The orbit is therefore nonperiodic and its states are distinct.
P221 makes Y_infinity finite; one fixed K works for all q. Distinct positive
integers escape every finite height, and `x_j/Y_j=2^(a_j+theta_j)` implies
`a_j->infinity`, hence `H_q->infinity`. These facts precede every limit below.

For any **fixed** integer k>=2, suppose H_q=o(q^(1/k)). Set r=k-1.
The ball is O_k((H+K)^k)=o(q), `(H+K)a_q=O(H^2)=o(q)`, and
E_q=alpha*q-a_q-theta_q=alpha*q+o(q). EDIT-CAP gives
`alpha*q <= 2(H+K)D/k+o(q)`. Dividing, using (H+K)/H->1, yields

```text
liminf H_q D_q/q >= k alpha/2.                         (P263)
```

Equivalently take a bounded realizing subsequence of HD/q; if none exists
the result is automatic. No uniformity in growing k is assumed. In
particular H=o(sqrt(q)) forces liminf HD/q>=alpha (twice P253's former
necessary constant). H=q^(o(1)) permits each fixed k and gives HD/q->infinity.
P253 remains valid; P254's monotone square-root frontier is not improved by
this argument at H comparable to sqrt(q).

For delta>0 define
`Psi(delta)=(2+delta)log_2(2+delta)-delta log_2(delta)-2`.
The binomial bound obtained from a single nonnegative term of (1+t)^N
gives, for r=floor(delta n),
`log_2 B(n,r)<=n Psi(delta)+O_delta(log n)`.
If H_q<=C log_2 q+O(1) and C Psi(delta)<1, this is o(q) in ordinary scale:
choose a fixed positive gap in the strict exponent inequality. Also
n a_q/(r+1)=O(H)=o(q), n/(r+1)->1/delta, and E_q/q->alpha. Therefore

```text
liminf D_q/q >= alpha delta/2.                         (P264)
```

For C=2, delta=1/16, `2 Psi(1/16)<1` is exactly `33^33<2^168`, verified as
an integer inequality; thus liminf D/q>=alpha/32. Finally Psi(delta)->0
as delta decreases to zero. If D=o(q) but H/log_2 q did not tend to infinity,
there would be an unbounded sequence of q with H<=C log_2 q for finite C.
The *same* fixed-K argument and strict entropy bound on that subsequence
would give positive liminf D/q there, a contradiction. Thus
`D=o(q) => H/log_2 q->infinity`. This proof covers bounded subsequences,
not just an eventually uniform upper envelope.

## 4. P265: exact oscillating formal model

This u is **not** the old Phase 13 square-root model. Starting with a_0=0,
p=0, set at odd index j

```text
h=max(16,2 floor(log_2(j+1))), b=f_(j+1)-f_j, d=f_(j+1)-f_p, r=a_j;
change=0;
if r<h-1: change=1 if b=2, else 0;
else if d>=r: change=-1 if r>=h, else (1 if b=2, else 0);
e_j=b-change; a_(j+1)=r+change;
if change!=0: p=j+1.
```

All log floors in the finite construction are decided by exact enclosures;
the theoretical definition uses exact real floors. Since b=1 never occurs
twice in succession (`3^2>2^3`), upward opportunities have gap at most two.
Increases occur only when b=2. Thus e is in {1,2,3}, a>=0, and telescoping
gives E_j=f_j-a_j. Every full prefix is coefficient-safe, since between odd
endpoints the minimum coefficient is at an endpoint.

The first 32 exponents are independently reconstructed using integer powers;
a_32=15. Up to the next target change the heights are 15 or 16. At each
subsequent target increase h->h+2 the defect is at worst new-h minus three.
The catch-up clause takes at most four steps to reach new-h minus one.
Successive target boundaries are separated by much more than four steps.
Before the boundary, a_j was never above the old target. During a fixed
target epoch, ordinary changes alternate h-1 -> h -> h-1, apart from this
bounded catch-up. Induction gives for j>=32

```text
2 floor(log_2(j+1))-3 <= a_j <= max(16,2 floor(log_2(j+1))).
```

In particular a_j=2 log_2 j+O(1), H_q=2 log_2 q+O(1), E_q/q->alpha.
For a constant-height run r begun at p, the first crossing of
f_(j+1)-f_p>=r occurs after r/alpha+O(1) odd steps (floor errors <1).
A required upward b=2 delays it by at most one more step. Hence a full
down/up pair in an unchanged target epoch lasts (2h-1)/alpha+O(1), with a
uniform O(1), and contains exactly one downward step.

There are O(log q) target changes. Their crossing pairs and catch-up portions
use at most O((log q)^2) steps; the final incomplete pair uses O(log q).
For j>=q/(log q)^2, h(j)/H_q->1 uniformly. The earlier portion has at most
q/(log q)^2=o(q/H_q) downward steps. Summing the completed recent pairs,
whose lengths are (2H_q/alpha)(1+o(1)) uniformly, proves

```text
D_q ~ alpha q/(2H_q), H_q D_q/q -> alpha/2, D_q=o(q).
```

### 4.1 Pure CAP is zero at every depth (origin u)

Use exactly P252's pure intervals, including the final possibly empty one.
At a usual threshold closing, the mechanical run first reaches r with
overshoot at most one. A downward closing adds a zero excluded from the
pure interval, so ell<=r+1. An upward closing can wait one b=2 step, then
deletes the final zero, so ell<=r+2. Catch-up runs last at most the pattern
1,2 in baseline gaps, deleting the final zero; their ell<=2. Before any
ordinary closing, an incomplete run has mechanical length at most r+1.
If a target changes meanwhile, catch-up resumes immediately; from the
previous partial run plus the next two-step opportunity the same r+2 bound
holds (a possible extra 1 wait is followed by deletion of the next zero).
Thus every pure interval has ell<=r+2, including at arbitrary cutoffs.
For K>=4 and every test height v>=r, `ell-v-K+1<=-1`; all P252 CAP
left sides are identically zero. This is an all-depth length proof, not
an extrapolation of the million-step maximum ell-r=2.

### 4.2 Real and 2-adic properties

Write c_j=3^j/2^E_j=2^(a_j+theta_j). The proved envelope gives
c_j=Theta(j^2) for j>=32, with constants independent of j. Therefore
`beta_infinity=sum 1/(3c_j)` converges. Direct exact calculation gives

```text
beta_32=1853052669542017/1853020188851841,
beta_infinity <= beta_32 + 480/(3*2^15)+1/96 <2.
```

The 480 terms cover 32<=j<=511, where a_j>=15. For dyadic shell
2^m<=j+1<2^(m+1), m>=9, each term is at most 8/(3*4^m), and there are
at most 2^m terms. The full tail is bounded by
`(8/3)sum_(m>=9)2^-m=1/96`. Double-counting a boundary only enlarges the
upper bound; no uncomputed tail is omitted.

E_j->infinity gives a coherent odd 2-adic source
`xi=-sum_(j>=0)2^E_j/3^(j+1)` in Z_2. At each suffix, its first term is
-1/3 and all later terms are even 2-adically, so the suffix source is odd;
the recurrence `3 xi_j+1=2^e_j xi_(j+1)` realizes the exponents *exactly*.
This establishes genuine 2-adic parity, not a positive ordinary source.
The real companion `h_j=c_j(beta_infinity-beta_j)` is Theta(j), because
the tail of a sequence bounded above and below by positive multiples of
1/j^2 is Theta(1/j). Thus sum 1/h_j diverges. Its suffix series dominates
`sum_(ell>=0)2^ell/3^(ell+1)=1`; every suffix contains an exponent >1,
so h_j>1 strictly. Critical density and summable inverse coefficients hold.

## 5. P266: extension, no-gain, and ordinary-source exclusion

For the original u define C_u as the sum over zero inputs of inverse prefix
coefficient. At a one input 1/c decreases by 1/(3c); at a zero input it
increases by 1/c. Telescoping gives `C_u=beta_infinity-1<1`, because
1/c at the terminal prefix tends to zero. Partial sums are nondecreasing.
For `w=110111111u` the initial one-run has length two. Its shifted zero-start
tail is `v=0111111u`. The initial zero contributes 1 to J/3^t, and the
coefficient of 0111111 is 729/128. Hence at **every** tail prefix

```text
J/3^t <= 1+(128/729)C_u <857/729<3.
```

A zero-starting tail of the same length and J but weight t+k, k>=1,
would contribute at least 3^(t+k) from its first zero, giving J/3^t>=3.
This is impossible. Neither all-same-Q nor all-Q geodesicity follows.
The pure-CAP origin in Section 4 is u, while this vertex is the tail of w;
the origins are not identified. NG45 survives and gets another formal model.

Suppose a positive ordinary S realizes all of u. Safety makes it nonperiodic
and distinct; beta_infinity<2 provides a **fixed** K>=4 with
2^K>=3(S+2), independent of P221. Apply P262 at r=1 for every q. Its left
side is alpha*q+o(q), its ball is O((log q)^2)=o(q), and

```text
(H+K)(a+2D)/2 = alpha*q/2+o(q).
```

Contradiction. Thus no such S exists. A positive realization of w would
reach a positive odd source for u after its finite prefix, also impossible.
This excludes the *specific* model, not every permanent-safe word.

### 5.1 Separate finite repeat-and-split rule

Two windows at i<j agree for at least n bits but split later. If a positive
source S realizes the prefix through that split, deterministic evolution
implies T^i(S)!=T^j(S), even if some other states repeat. If both values are
strictly below 2^n, P125 contradicts their matching n bits. For S<=2^B the
checker verifies the height at each of these starts by its **exact affine
formula**, in addition to checking K and the conservative model envelope.
No global distinctness premise is used in these eight certificates. Prefix
length minimality is not claimed. Source exclusion for all B is the written
argument above, not extrapolation of eight finite examples.

## 6. P267: optional finite pre-repeat sparsity, separate from P262--P266

Let F(X) be the supremum occupancy of any integer interval [a,a+X) by any
finite **pairwise distinct positive trajectory** x_0,...,x_(m-1), with
x_(j+1)=T(x_j) inside the segment. X>=1 is an integer; a is arbitrary.
Certainly F(X)<=X. At N=ceil(log_2 X), discard its last min(m,N) states.
The remaining sources have N-step images inside the same distinct segment.
Equal-time images of these sources are distinct because their indices are
distinct and still within the segment; future merging beyond the segment
is irrelevant. For each odd count s, the images lie in one translated
interval of length 2*3^s by P219. They form a subset of this trajectory,
so their occupancy is at most F(2*3^s). P125 bounds the high-count part by
the number of its parity vectors. Therefore

```text
F(X)<=N+sum_(s<=floor(14N/23)) F(2*3^s)+2^(N H_2(14/23)).
```

Induct on integer X with rho=29/30. For N>=135 all recursive arguments are
smaller. The exact inequalities
`3^14<2^23`, `23^690<2^667 14^420 9^270`, and
`24^690 3^(406*135)<=2^(667*135)` give respectively compression, high-count
entropy, and a low-part allowance <16X^rho, as in P220. The last inequality
persists since 3^406<2^667. The high part is <2X^rho. Also N<X^rho: at 135
this follows from `135^30<2^(134*29)`; thereafter (N+1)/N<=136/135<3/2
and `(3/2)^30<2^29` preserve it. Thus the extra tail cost leaves
F(X)<19X^rho<32X^rho. For N<135, X<=2^134<32^30 gives the bound trivially;
X=1 is immediate. Consequently **F(X)<32X^(29/30)**.

This does not apply P220 unchanged to a convergent orbit's value set. Such a
set need not be equal-time collision-free after observation ends. The new
terminal loss is essential to this proof. This supplement supplies no new
capacity table, optimized constant 13, or cycle exclusion, and is not an
input to the other new results.

## 7. E60: finite audit and reproducibility boundary

The independent model has q=1,000,000, E=1,584,925, a=37, H=38,
D=22,149, U=22,186, t=44,335, 44,336 pure intervals, maximum ell-r=2.
Its binary byte word SHA-256 is
`e6b23f4402a336c2097f296064e67dc983d5fe227ba63f0b3039f2091abe233f`.
The exponent digest in our JSON uses compact JSON integer-array encoding,
not the proposal's raw byte encoding; word and numerical statistics agree.

At S<=2^16 use K=21,n=59: M=1,584,867 windows, total charge 2,592,868
versus upper bound 2,615,765. There are 590,784 occurrences with at most
one edit but only **966 distinct words** (general ball upper bound 7,320).
EDIT-CAP at r=1 has RHS 1,315,202 and excess 269,665. This is a formal-word
incompatibility with distinct small positive states, not an observed integer
orbit violating a theorem. The eight separate repeat certificates have
source exponents 8,16,32,64,128,256,512,1024 and required prefix lengths
217,217,217,386,1269,1269,3142,25756 respectively.

Exhaustive finite domains: 24 edit balls (n=1..8,r=0..2), 1,364 exponent
words (q=1..5,e=1..4), 10,691 width cases, 59,372 low-edit memberships;
256 odd sources S<=511, at most 64 complete odd blocks, 5,090 valid
prefix queries, 3,888 with positive windows, 735 coefficient-safe prefixes,
20,360 exact capacity comparisons. The first nonvacuous safe case is S=27,
q=7; the first unsafe one is the single traversal 1->2->1, whose distinct
input states and repeated closing endpoint are legal. Its second traversal
is rejected. Intermediate even-state repetition is checked, not just odd
boundary repetition. The inherited 61 word-family rows and 22 named
controls are recomputed and checked; all 61 family sources and 24 additional
ordinary family sources receive the new edit-capacity prefix audit. NG46's two all-length
potentials are rechecked, not merely hash-compared.

See [run results](../../../PHASE44_RUN_RESULTS.md) for exact commands,
test scope, clean-worktree acceptance commit and manifest. The supplied ZIP
SHA-256 is `f5556a904b9507810e1131ff53d263d4ea4f43deeb0192a917d20c2b29d96998`;
all eight supplied member hashes were checked before any computation.

## What this result does not prove

H112, H72, H89 and H133 remain `OPEN`. There is no contradiction for all
superlogarithmic maximum defects, or for logarithmic defects with sufficiently
large downward variation. Many symbolic edits have not been shown to force
an ancestor satisfying the fixed source's 3-adic carry, literal positivity,
and coefficient/source dominance. Finite geodesic monotonicity is still
refuted by NG46; P254 retains its premise. Neither the 2-adic model nor its
exclusion is a Collatz counterexample or a Collatz proof. Arbitrary-area
positive-cycle exclusion remains a separate obligation.

Next target: a source/lift-linked **upper** variation budget contradicting
P263/P264, or an obstruction to P258-compatible certificates at every prefix
of one fixed ordinary source. Another symbolic model or finite depth increase
without that arithmetic link does not meet this acceptance boundary.
