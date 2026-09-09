# Phase 41 audit: complete shifted decoding and all-Q ancestors

Date: 2026-09-09. Base: `4a814b3b376d491e602310e41cbf30725f9fd5b6`.
The attachment is an unaudited proposal, not an external theorem. This audit
rederives its arguments and uses separately implemented finite reconstruction.
`proves_collatz=false`. The N labels in the proposal are not repository IDs.

## 1. Conventions, dependencies, and classification

Throughout, `T(n)=n/2` for even n and `T(n)=(3n+1)/2` for odd n.
Bits describe **input** parity in chronological order. For a word w, L is
length, q is its number of ones, and

```text
F_w(x)=(3^q x+B_w)/2^L, c(w)=3^q/2^L,
D(w)=B_w+2^L-3^q.
```

D here is the shifted correction, not a cycle denominator. Empty words
have L=q=B=D=0 and c=1. A safe word has c(p)>=1 at every prefix p; every
nonempty safe prefix actually has c(p)>1, by unique factorization.
Nonperiodic means **not eventually periodic**. Ordinary sources are positive
integers, not just compatible 2-adic residues. Tails at a shifted vertex
include their initial zero.

- P242/P243: extend the existing height notation to even inputs and supply
  a shorter global-minimum proof. This is a reorganization of the Phase 40
  reduction, not a second independent route or a new Collatz breakthrough.
  The converse below makes H112 equivalent to nonperiodic exclusion.
- P247 `VERIFIED_THEOREM`: the unrestricted-Q maximum coefficient ratio
  along a fixed nonperiodic orbit exists and eventually stabilizes, without
  a supplied effective last-coalescence index.
- P248 `VERIFIED_THEOREM`: complete shifted decoder for every (L,q,D).
- P249 `VERIFIED_THEOREM`: mixed 2/3 literal coalescent rewriting, with even
  competitors and the different least-source/height-minimum scopes retained.
- P250 `VERIFIED_THEOREM`: safe-target gain cap and finite vertex cutoff.
- P251 `VERIFIED_THEOREM`: the square-root formal word admits no larger-weight
  tail at its shifted vertex at any depth.
- NG44 `REFUTED`: weights in a shifted fiber need not form an interval.
- NG45 `REFUTED`: the current formal analytic conditions do not force an
  eventual higher-weight same-vertex rewrite. This is a narrow formal no-go,
  not a counterexample to H112 or to a positive-integer-only statement.
- E57 `VERIFIED_FINITE`: the precise bounded reconstructions in Section 10.

Inputs are the internal P221 reciprocal summability theorem, P115's exact
infinite-source lift criterion, P242/P243's canonical positivity bridge, and
the Phase 13 Section 6 model, whose estimates are rederived below. No new
external theorem is used, and no literature-wide novelty claim is made.
P206 remains a different decoder on a critical-safe modular image.

## 2. P242/P243: all-positive normalized-height reproof

Let N be the set of positive ordinary integers with nonperiodic future.
For n in N put x_k=T^k(n), with q_k odd inputs before k. The exact finite
identity is

```text
Y_k(n)=2^k x_k/3^q_k
      =n prod_{0<=j<k, x_j odd}(1+1/(3x_j)).
```

P221 applies to this injective orbit. Thus sum 1/x_j converges and the
displayed product has a finite positive limit. An infinite positive orbit
has infinitely many odd inputs (division by two cannot continue forever).
In particular at least one strictly positive correction occurs, even if n
itself is even. Hence

```text
Ycal(n)=lim_k Y_k(n) is finite and Ycal(n)>n.
```

Shifting the finite normalization by one step and taking its convergent
limit proves the exact cocycle

```text
Ycal(T(n))=a(n)Ycal(n), a(even)=1/2, a(odd)=3/2.
```

Consequently every positive literal finite path a from z to y, with
nonperiodic common future, satisfies `Ycal(y)=c(a)Ycal(z)`; no safety or
odd-source hypothesis is used.

Assume N is nonempty. Choose n0 in N. The nonempty sublevel set
`{n in N:Ycal(n)<=Ycal(n0)}` is contained in the finite set of positive
integers below Ycal(n0). A minimizer S* on this sublevel is also a global
minimizer on N. This is finite attainment, not well-ordering of the reals.
For every actual prefix d from S* to y, y also belongs to N; therefore

```text
c(d)=Ycal(y)/Ycal(S*) >= 1.
```

This proves full permanent safety directly and forces S* odd. If any
positive literal competitor a from z reaches the same y, then z belongs
to N, so `c(a)=Ycal(y)/Ycal(z)<=c(d)`. This includes even sources, unsafe
paths, different Q, longer paths, and empty paths at any endpoint.

Global minimization over all nonperiodic sources removes the need for
strict-valley extraction in this particular existence proof. It does not
invalidate Phase 40's classwise minimization or the useful valley algorithm
for a supplied unsafe witness. It does not assert ordinary-source descent
for an arbitrary height-improving competitor.

### Exact logical position of H112

The canonical-positive endpoint bridge in Phase 40 Sections 3--4 turns
every shorter safe same-Q endpoint-class word into a positive literal
competitor. Hence every prefix of S* is an H112 geodesic. Because S* is one
fixed positive ordinary source, P115 forces eventual zero canonical lifts,
contrary to H112. This rederives P243 without X02.

Conversely, if H112 fails, its infinite safe all-prefix same-Q-geodesic
branch has only finitely many nonzero canonical accelerated lifts. P115
then realizes the entire branch by a fixed positive ordinary integer.
An eventually periodic positive realization cannot be permanently safe:
on a period of length L>0 and q>0, `x=(3^q x+B)/2^L` with B>0 implies
`3^q/2^L<1`. Repeating that period makes the total prefix coefficient tend
to zero, contradicting safety. A positive cycle cannot have q=0, since
repeated halving strictly decreases positive values. Thus this realization
is nonperiodic. We have the internal logical equivalence

```text
H112  iff  no positive ordinary nonperiodic shortcut orbit exists.
```

This is an equivalence with an unresolved global branch, not its proof.
Positive nontrivial cycles remain separate. No new claim number is assigned
to the P243 reformulation; the expanded statement and audit date are recorded
without changing its status or H112's OPEN status.

## 3. P247: all-Q maximum ratios stabilize non-effectively

Fix any S in N and its odd endpoints x_q, with actual prefix d_q. No
permanent-safety assumption on S is needed. Let R_q be the supremum of
`c(a)/c(d_q)` over all positive literal paths a to x_q, of any length and
weight, including the empty path. The actual path gives ratio one.

For every ratio at least one the cocycle gives

```text
c(a)/c(d_q)=Ycal(S)/Ycal(z),  z<Ycal(z)<=Ycal(S).
```

There are finitely many possible positive sources z, uniformly in q.
For each such z and endpoint, the path is unique: two visits to the same
endpoint would make z eventually periodic. Once a source joins the chosen
future it remains a candidate at all later odd endpoints, and its ratio
is unchanged by a common suffix. Thus R_q is an attained maximum of a
nonempty finite set of ratios, is nondecreasing, and eventually constant.
An initial even segment before the first odd endpoint changes none of this.

The values can be rational even though their expression via Ycal uses
limits. We have not supplied an effective numerical bound on Ycal(S), an
effective bound on all join times, or a recognizer of the last join. A
finite plateau is not a certificate. Allowing all Q does not fix this gap.

## 4. P248: complete shifted decoder

If the odd positions are `p_0<...<p_(q-1)`, independent expansions give

```text
B_w=sum_j 2^p_j 3^(q-1-j),
D(w)=sum_{i: w_i=0} 2^i 3^(number of ones strictly right of i).
```

Alternatively telescoping `D(w1)=3D(w)` and `D(w0)=D(w)+2^L` proves the
second formula. Prepending a bit now gives

```text
D(1v)=2D(v),   D(0v)=3^q(v)+2D(v).
```

The parity of D therefore determines the first bit uniquely. Given
integers L,q,D, reject negatives and q>L. At every step:

1. If D is even, a valid word must start with one. Require q>0; replace
   `(L,q,D)` by `(L-1,q-1,D/2)`.
2. If D is odd, it must start with zero. Require `D>=3^q`; replace it by
   `(L-1,q,(D-3^q)/2)`.
3. Reject when remaining q is negative or exceeds remaining L. At L=0,
   accept exactly q=D=0.

Induction on L proves both necessity and sufficiency, including all invalid
images, and uniqueness. L=q=D=0 gives the empty word. D=0 is valid exactly
for all-ones words q=L. q=0 is valid exactly for the all-zero value
`D=2^L-1`. Positive D left at termination, depleted q with an even D,
and an early zero remainder with q<L are rejected. Noninteger API inputs
are also rejected; they are outside the mathematical domain.

Maintaining 3^q and dividing it by three when q decreases uses O(L)
arbitrary-precision integer operations, in addition to constructing the
initial power. This is **not** linear bit complexity: D may be very large.
The independent verifier never uses this leading-bit recursion; it
constructs the finite image from the two positional sums.

## 5. P249: mixed source rewrite and minimality scopes

Let `w=1^R v` be an actual finite prefix from positive S, with R>=0
maximal and v beginning with zero, length ell, weight t, shifted correction
J. Then `v2(S+1)=R`. Let v' begin with zero, have the same ell,J and
weight t+k with k>0. For an integer `0<=h<=min(R,k)`, put

```text
g=2^h 3^(k-h),   z=(S+1)/g-1,   w'=1^(R-h)v'.
```

Assume g divides S+1 and z>0. Direct shifted affine substitution gives

```text
F_w(S)+1 = 3^(R+t)(S+1)/2^(R+ell) + J/2^ell
          = F_w'(z)+1,
c(w')/c(w)=g>1,     0<z<S.
```

The endpoint is an integer. Final affine integrality forces the initial
parity: reducing the numerator modulo two distinguishes an odd from an even
first bit. Applying that branch and inducting proves every declared bit is
literal. Positive T preserves positivity. Safety is a separate property.

When h=R, `(S+1)/(2^R 3^(k-R))` is odd, so z is even. These competitors
must be retained. For example `5 --100--> 2` and `2 --01--> 2` have gain
two, R=h=1; neither path needs to be safe for the algebra.

For the least ordinary positive counterexample (if any), a smaller positive
coalescing z is already impossible, whether the common future is cyclic or
nonperiodic, and whether w' is safe or unsafe. For the global normalized-
height minimum of Section 2, the nonperiodic common future and g>1 give
the contradiction instead. These are different hypotheses and orders.

If `3|(S+1)`, the positive integer `z=(2S-1)/3` is odd, is smaller than
S, and satisfies T(z)=S with coefficient 3/2. Thus a least ordinary
counterexample or global nonperiodic height minimizer is already excluded
by this elementary predecessor. The extra ternary factors in the mixed
formula alone do not settle the hard minimal-source cases.

## 6. P250 and NG44: cap, cutoff, and holes

For a coefficient-safe target w of weight Q=R+t, the normalized additive
correction is

```text
beta=B/3^Q=sum_{odd positions i} 1/(3 c(w[:i])) <= Q/3.
```

Since the final coefficient c>1 and `D(w)=2^R J`,

```text
J/3^t=(3/2)^R (beta+1/c-1) < (3/2)^R Q/3.
```

The first-zero term of a competing tail with weight t+k is `3^(t+k)`,
so `J>=3^(t+k)`. Combining these two inequalities proves, exactly,

```text
3^(k+1) 2^R < 3^R Q.
```

In particular `Q<=3*2^R` forces k<R. For every fixed vertex, regardless
of safety, no weight t with `3^t>J` is possible. The implemented complete
fiber query tests **every** t until this cutoff or t=ell; it does not
assume intermediate weights are attainable.

Indeed at ell=14,J=24573 the complete fiber is

```text
t=1: 00000000000001
t=2: 01000000000001
t=5: 00001101001100
t=6: 01001101001100
```

No t=3,4 word exists. E57 independently checks every shorter zero-prefixed
tail: there are no holes through ell=13. At ell=14 there are two hole
vertices, 24573 and 24609; the latter has weights {3,4,7,8}. Thus NG44's
least (ell,J) is (14,24573). This is finite minimality in the declared
ordering, not an all-depth classification of holes or gain-budget failures.

## 7. P251/NG45: an all-depth maximal-vertex formal word

Reconstruct the Phase 13 Section 6 model using exact powers, not a rounded
logarithm. Define

```text
f_j=floor(j log_2 3), b_j=f_(j+1)-f_j, A_0=0;
A_(j+1)=A_j+1 if b_j=2 and A_j<floor(sqrt(j+1)), else A_j;
e_j=b_j-(A_(j+1)-A_j), E_j=sum_{r<j}e_r=f_j-A_j.
```

The inequalities `2<3<4` and `3^2>2^3` prove b_j in {1,2} and rule out
consecutive b_j=1. The target floor(sqrt(j)) increments only at squares.
At the first square, A_1=0 and A_2=1. At each later square m^2, the
preceding target m-1 has already been attained, since two consecutive
opportunities cannot both lack b=2. The new target m is attained at that
square or the next time, before the following square. Between squares no
further increment occurs. Induction proves

```text
floor(sqrt(j))-1 <= A_j <= floor(sqrt(j)),   e_j in {1,2}.
```

At the j-th odd input of u, the coefficient is
`c_j=3^j/2^E_j=2^(A_j+theta_j)`, where `0<=theta_j<1`.
Every complete odd block is `1` or `10`; the intermediate odd step
increases its coefficient, and the coefficient after a full block is at
least one. Thus all full shortcut prefixes of u are safe. For an e_j=2
block, its only zero has coefficient (3/2)c_j just before that zero. Its
contribution to the normalized zero correction is therefore 2/(3c_j).

Using the square-shell bound, including j=0,

```text
C_u=sum_{zero positions i of u} 1/c(u[:i])
   <= (4/3) sum_{j>=0} 2^(-floor(sqrt(j)))
    = (4/3) sum_{m>=0} (2m+1)/2^m = 8.
```

The last equality uses the exact geometric identities sum 2^-m=2 and
sum m2^-m=2, not a floating approximation. Let

```text
w=11 0 111111 u,   v=0 111111 u.
```

The prefix 110 has coefficient 9/8>1, its later six ones increase it,
and u is safe; hence w is permanently coefficient-safe. For any prefix
of v containing only its initial zero and some of those six ones,
`D/3^t=1`. After the six ones, u's zero terms are scaled by `2^7/3^6`,
giving at every subsequent prefix

```text
D(v_prefix)/3^t <= 1+(128/729)C_u <= 1753/729 < 3.
```

A larger-weight zero-prefixed tail at the same (ell,J) would require
`J/3^t>=3`. This is impossible **at every depth**, by the convergent sum
bound, not by the 512-step check.

### Analytic conditions and 2-adic realization

Here `E_j/j -> log_2 3`, and `A_j` tends to infinity with
`sum 2^-A_j<infinity`. Consequently the full-word discrepancy tends to
infinity as well. The irrationality of log_2 3 follows from unique
factorization. An eventually periodic binary word has rational odd-bit
density, whereas u has density `1/log_2 3`; u and w are not eventually
periodic.

The inverse series `-sum_j 2^E_j/3^(j+1)` converges in Z_2 because E_j
tends to infinity. The same construction at each suffix gives an odd
2-adic number, since its first term is odd and all later terms are even.
The exact recurrence makes the next exponent exactly e_j, not just at
least e_j. Prepending the finite full word gives the unique coherent odd
2-adic source for w. None of this establishes a positive ordinary source.

The real companion series is

```text
h_j=(1/3) sum_{n>=0} 2^(E_(j+n)-E_j)/3^n.
```

Writing m=floor(sqrt(j)), each term before the factor 1/3 is at most
`4*2^(m-floor(sqrt(j+n)))`. Summing entire square shells, even when the
first shell is only partially present, gives

```text
h_j <= (4/3) sum_{r>=0}(2(m+r)+1)2^-r = (16m+24)/3.
```

All e>=1 makes h_j>=sum_n(2/3)^n/3=1. Infinitely many e=2 remain,
because the number of b=2 is linear while A grows only as a square root;
therefore h_j>1 at every suffix. The upper bound implies sum 1/h_j
diverges. The finite prefix before u changes finitely many odd terms;
its odd exponents are also 1 or 2, so h>1 is preserved backwards.

Thus permanent safety, critical density, discrepancy escape, inverse-
coefficient summability, coherent 2-adic realization, h>1 and sum 1/h
divergence are all compatible with **no same-vertex improvement ever**.
NG45 refutes only a proposed existence assertion based on those formal
conditions. Full same-Q geodesicity, all-Q coefficient maximality, and a
positive ordinary source have not been established for this word. H112
is not refuted. Haar-nullness or distinct real/2-adic limits is not an
integer-exclusion proof.

## 8. The convergent source-7 control

For positive inputs 1,3,7, let chi be L-2Q along the trajectory to its
first 1. Direct traces give chi(1)=0, chi(3)=chi(7)=1. Later turns around
the cycle 10 contribute zero to chi.

Source 7 has S+1=8 and initial run R=3. Any mixed rewrite would have
k=h in {1,2,3}, because no ternary factor divides 8. For k=3 the source
is zero and is inadmissible; k=1,2 give z=3,1. A common endpoint would
require

```text
chi(7)-chi(z)=(L-L')-2(Q-Q')=2k-h=k.
```

The actual differences are respectively 0 and 1, not 1 and 2. Appending
a common suffix to the first future 1 preserves this identity, including
any cycle repetitions. Thus source 7 admits no mixed same-vertex rewrite
at any prefix. It converges and is not a permanent-safe counterexample.

## 9. Broader ancestor oracle and its missing existence theorem

For a positive endpoint y and candidate positive z, length L', weight q',
the required shifted correction is exactly

```text
D'=2^L'(y+1)-3^q'(z+1).
```

P248 decides this single finite candidate completely. Acceptance also
checks its entire literal positive trajectory. Strict coefficient dominance
over a target (L,q) is the integer comparison
`3^q' 2^L > 3^q 2^L'`.

Since B'>=0 even for an empty path, `y>=c' z>c_target z`. Thus all
strictly dominating sources obey

```text
1<=z<y/c_target, equivalently z<=(y*2^L-1)//3^q.
```

This is an effective finite source bound at a specified endpoint. It
does **not** bound all ancestor lengths or weights. Our exhaustive oracle
always declares its competitor-length cap and includes every q' from 0
to L', even z, empty paths, longer competitors, and different vertices.
The independent checker simply runs each positive source forward and
selects every matching endpoint/length. It never calls the decoder.

The control `31 --empty-->31` is strictly dominated by
`27 --110-->31` with L'=3,q'=2,c'=9/8; a target-length or same-Q filter
would miss it. NG25's higher-Q and lower-Q examples, NG26's unsafe path,
NG28's negative carry, and both NG43 witnesses are preserved individually
outside the small exhaustive oracle range as required.

What is still needed is an **existence theorem**, not another decoder:
for every hypothetical positive ordinary nonperiodic minimal-height orbit,
force a literal positive coalescing ancestor of strictly greater coefficient
at some prefix, or prove the equivalent H112 nonzero-lift assertion. Such
an argument must use ordinary positivity, carry, ancestry, source order,
or comparable cross-address arithmetic absent from NG45. Same-vertex
maximality alone is insufficient. No effective universal L',q' cap or
all-Q no-hit certificate is supplied here. Arbitrary-area positive cycles
remain a separate obligation.

## 10. E57 finite reconstruction and provenance

The declared domains and independently matching results are:

| Check | Exact finite scope and result |
|---|---|
| Decoder | All 32,767 binary words of lengths 0..14 |
| Invalid/boundary images | L=0..7; q=-1..L+1; D=-1..max(1,3^max(0,L-1))+1; 255 valid and 10,291 rejected triples |
| Fibers | Every zero-prefixed tail through ell=14; no holes through 13; two hole vertices at 14 |
| Mixed rewrites | ell=1..8, R=0..6, v3(S+1)=0..2, every higher fiber weight and admissible h; 4,192 rows, 658 even-source rows |
| Gain cap | 645 safe-target rows; zero unsafe alternatives in this small scope, not generalized past NG43 |
| Formal model | 512 odd steps of u, total word length 798, ten nested-source checkpoints; eight changes between these checkpoints |
| Ancestors | 125 target instances; all dominating positive sources, every L'=0..10 and q'=0..L'; 718 hits |
| Controls | Six mandatory families; NG22/24/25/26/28/43, source 167 and source 7; both original and lex-first NG43 witnesses |

The generator uses affine propagation, leading-bit decoding, CRT source
construction, and explicit candidate enumeration. The verifier reconstructs
odd/zero position sums, finite image maps, ordered ordinary source lifts,
power-comparison exponents, bit-lifted source cylinders, and direct forward
trajectories. Sharing basic integer arithmetic and the stated finite domain
is not claimed as proof of independence; the relevant algorithms differ and
the verifier imports no search code. The tests reject altered arithmetic,
scope, omission, proof flags, statuses, and added fields. Written infinite
proofs are not inferred from the finite certificate or described as formal
proof-assistant verification.

Provenance: the ZIP's eight SHA256SUMS entries all matched its members;
the standalone prompt matched the bundled prompt. The input hashes are

```text
bundle.zip  cfeb5d813c37aa18f17b069817df4ed5a055669975ca12993613d98fcc40e73c
CODEX_PROMPT_JA.md  92b6cc78e41c30b79e7d68c9eb334f65ec01198bce72903542307793f58c4ed6
RESEARCH_NOTE_JA.md  c0ca230a10a6caa05f976827db467bbe20ac33bea51f8a0ec7ec14f2e2b48fc1
shifted_decoder_audit.py  fa8c380c2c6c00b4a00c02a4133725eed1cd46511eea3b89c251f186d0094785
```

The supplied C++ length-27 output remains an unaudited single-implementation
finite computation. It was read but not executed, imported as accepted
evidence, or promoted to a theorem. Source provenance hashes are not a
mathematical validation of that input. The accepted independent work is in
[`../../../src/phase41_search.py`](../../../src/phase41_search.py),
[`../../../verifier/verify_phase41.py`](../../../verifier/verify_phase41.py),
and the [`run report`](../../../PHASE41_RUN_RESULTS.md).

## What this result does not prove

It proves neither H112/H72/H89/H133 nor Collatz. The formal model has no
verified positive ordinary source, and its no-gain property covers only a
single shifted vertex at each depth. All-Q ratio stabilization is not an
effective stopping rule. A finite residue plateau or ancestor no-hit is not
an infinite certificate. Mixed divisibility and complete decoding provide
tests, not the missing existence of a successful ancestor. No cycle branch
is closed by the normalized-height proofs. `proves_collatz=false`.
