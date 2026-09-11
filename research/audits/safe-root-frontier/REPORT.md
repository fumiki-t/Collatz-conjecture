# Safe-root-frontier supplement — independent audit

Date: 2026-09-12. Base: `20907aad336a9634abca9f5bc467659559307af6`.
Primary obligations: H112/H72; both remain `OPEN`. Latest numbered phase: 44.
`proves_collatz=false`. The supplied R1--R6 labels are proposal-local, not
claim IDs. The [ledger](../../../docs/CLAIMS_LEDGER.md) is authoritative.
The [proposal](PROPOSAL.md) is preserved as submitted mathematical text;
the acceptance boundaries and corrections are in this audit and the
[run record](../../../SAFE_ROOT_FRONTIER_RUN_RESULTS.md).

## 1. Definitions, scope and dependencies

For positive ordinary integers use T(x)=x/2 when even and (3x+1)/2 when odd.
Bits are chronological **input** parities. For a word w of length L, with
q ones at positions 0<=p_0<...<p_(q-1)<L, put

    F_w(z)=(3^q z+B_w)/2^L,
    B_w=sum_j 3^(q-1-j) 2^p_j,       c(w)=3^q/2^L.

A word is safe iff every nonempty prefix has c>1; the empty word is safe.
The canonical source residue is -B_w*(3^q)^(-1) modulo 2^L. Integer source
and final value imply every branch is literal: reduce the affine numerator
modulo 2, recover the first parity, then induct on the suffix. Positivity
is preserved by each literal branch. No formal 2-adic source is promoted
to an ordinary positive source here.

Fix an actual target path S --d--> y with gamma=c(d). An improvement is a
positive literal path z --a--> y with c(a)>gamma, or with c(a)=gamma and z<S.
This is LEX, coefficient first and smaller source second. All lengths, Q,
even and unsafe sources, empty paths and cyclic revisits are in the domain.
If gamma<1, the empty path at y improves. Gamma=1 for an actual word forces
the empty target, by unique factorization. Below assume gamma>=1 and set
H=y/gamma, b=ceil(H)-1.

Internal inputs: P87 (valley extraction), P97 (safe correction bound),
P125/P248 (literal cylinders/decoding), P242/P243 (intrinsic height),
P257--P259 (earlier all-length barrier), and P271 (safe-word counts).
No new external theorem, EXT08, X02, random-parity assumption, or novelty
claim is used. The infinite arguments below are written derivations, not
proof-assistant formalizations; E65 checks their specified finite components.

## 2. P281 — global LEX safe reduction (proposal R1)

Every nonempty improvement has q>=1 and B>0, hence

    z=y/c(a)-B/3^q < y/c(a) <= H.

An empty improvement is impossible for an actual target with gamma>=1.
Consider any unsafe improvement and all its prefix coefficients, including
the initial 1. Distinct prefix coefficients are unequal: an equality would
give 3^r=2^s with a positive time difference s. The minimum mu<1 is unique,
proper, and not terminal, since terminal c(a)>=gamma>=1. Cut at this minimum.
Every nonempty suffix-prefix coefficient is strictly >1, and the suffix has
coefficient c(a)/mu>gamma. Its source v is an actual positive intermediate
integer. Its positive affine correction implies v<y/(c(a)/mu)<H, and its
odd count is no greater than that of a. Thus existence of any LEX improvement
with at most Q odd inputs is equivalent to existence of a safe one with at
most Q odd inputs. The reverse implication is inclusion of domains.

This is a **global source-set** statement, not equivalence at the same
source and not a listing of every unsafe path. Example: 6 --011--> 8 is
unsafe; 3 --11--> 8 is its safe replacement. The replacement need not be
smaller than the original target S. After any safety crossing we can discard
that rooted history only because all other positive candidate roots are
covered as well. P87 is reused; the new part includes the LEX tie and Q cap.

## 3. P282 — sharp safe extrema and exact fixed-Q windows (R2/R3; backlog B1)

For q>=1, a safe word of length L exists iff q<=L and 3^q>2^L. Necessity
is immediate; the word 1^q 0^(L-q) proves sufficiency. Before the (j+1)-st
one, safety says 2^p_j<=3^j. Thus, writing f_j=(3^j).bit_length()-1,

    p_j <= f_j,          p_j <= L-q+j,
    p*_j=min(f_j,L-q+j).

For j=0 the empty-prefix equality gives p*_0=0. Both upper-bound sequences
increase by at least one at every increment of j, so does their minimum.
The resulting positions lie in [0,L), obey every pre-one safety bound, and
terminal safety controls the last zero run. They therefore form a valid safe
word. Each summand in B increases strictly with its position, proving the
unique maximum. Adjacent interchange 01 -> 10 decreases B by the positive
quantity 2^p 3^(number of subsequent ones) and moves a one earlier, preserving
safety. Repetition gives the unique minimum 1^q 0^(L-q). Consequently

    B_min=3^q-2^q,
    B_max(q,L)=sum_(j=0)^(q-1) 3^(q-1-j) 2^min(f_j,L-q+j).

For endpoint y, write A=3^q and M=2^L. Every safe positive source is in

    max(1,ceil((My-B_max)/A)) <= z <= floor((My-B_min)/A).

For q>=2, the first two bits must be 11 (10 crosses at step two), so z=3
modulo 4. For q=1 the only safe word is 1, and z is odd. The empty q=0 case
is separate. From 2^p_j<=3^j each contribution B/A is at most 1/3; for q>=2
there is strict inequality. Since B_min>0, the real window has length <q/3.
It has at most floor(q/12)+1 points of the required mod-4 class for q>=2.

For a candidate z, force B=My-Az and decode its positions. The smallest
position is v2(B), since that term has odd multiplier and all later terms
have larger valuation. Subtract 2^p 3^(q-1), repeat, demand strictly increasing
positions below L, zero remainder, and full safety. This is an exact, complete
test, not merely an interval membership test. The independent checker instead
iterates the literal source and recomputes q and all prefix coefficients.

For any nonempty improvement gamma<=3^q/2^L<y, where equality at gamma is
allowed only for the smaller-source tie. The allowed length band is

    q log2(3)-log2(y) < L <= q log2(3)-log2(gamma).

Its width is log2(H). All decisions use powers, integer comparisons and bit
lengths, not logarithmic floating point. A simple enumeration of all L=O(q)
with O(q) candidate sources and O(q) integer operations per decode costs
O(Q^4) integer operations. Restricting to the band gives
O(Q^3(1+log H)) such operations, with reusable integer powers. These are
**not bit-complexity** estimates; endpoints can have arbitrarily many bits.
The implemented `scan` exposes `complete_all_Q=false`, even after no hits.
Generic gamma=1 with an artificial tie bound S>y separately admits the empty
equal-smaller witness; this situation is not an actual target of coefficient 1.

## 4. P283 — finite cover and all-length LEX soundness (R4/R5)

Let N=bit_length(b), with N=0 at b=0, so b<2^N. Explore the full binary
parity tree and terminate a leaf when its source cylinder misses [1,b],
when its coefficient first drops below 1, or at depth N. The latter safe
leaf contains exactly one candidate integer. Every positive candidate has
one leaf; empty and crossing leaves exclude no safe continuation. Check
possible target hits at **every prefix**, not only at leaf endpoints.

If U_k is P271's safe-word count, there are at most U_N surviving roots and
at most 1+2 sum_(k<N) U_k tree vertices. With mu=2^rho>1 from P271, split
this sum at N/2 and use a geometric sum to obtain

    vertices, surviving roots = O(H^rho/(1+log2(H))^(3/2)).

Small H is absorbed in the constant. This counts the initial tree only.
It is neither a bound on future trace length nor an application of P272's
permanent-source count to arbitrary trajectory values.

Trace each surviving literal root z from time zero, with coefficient c_k and
Y_k=x_k/c_k. Exact normalization gives Y_k=z+B_prefix/3^q; it is nondecreasing,
strictly increasing at odd inputs. After checking all earlier target hits,
one of these cuts is sufficient:

- c_k<1: only safe continuations at this root are excluded; P281 supplies the
  global equivalence and the complete cover treats their safe alternatives.
- Y_k>H, or Y_k=H with z>=S: at a later hit, c=y/Y<=gamma, and the tie cannot
  improve. **Y_k=H with z<S is not a cut.** Even steps preserve Y and may
  reach y with equal coefficient and smaller source.
- A first hit at y is nonimproving: a later return to y is a positive cycle.
  Any such nonempty cycle has q>0,B>0, so (2^L-3^q)y=B>0. Its coefficient
  is <1, making every subsequent return worse. No list of known cycles is
  assumed, and even/empty paths are included.

The finite certificate checker reconstructs positional affine maps, source
residues, prefix-freeness, exact Kraft sum (scaled by 2^N), all short prefix
hits, unique surviving roots, literal traces, earlier hits and cut conditions.
It also independently checks the integer diagnostics. On acceptance, no LEX
improvement exists over **all** positive sources, finite lengths and Q.
Finite certificates are sufficient, not necessary for arbitrary inputs of a
resource-bounded program. Budget exhaustion is `UNKNOWN` and is rejected.
Improvement `work` is nonnegative search telemetry, not a proof of a runtime
bound. The evidence verifier separately binds each expected target/query.

## 5. P284 — minimizer completeness and a finite unresolved minimum set (R6)

Assume the set of positive nonperiodic sources is nonempty. P242 gives finite
intrinsic height Ycal(n)>n and Ycal(y)=c(w)Ycal(z) for positive literal paths.
Height sublevel sets are finite, so a minimum h0 exists and its realizing
set M is a finite nonempty set of ordinary integers. Choose its smallest
source S*. An unsafe prefix would give a future source of height <h0;
thus every prefix is safe. A strict coefficient improvement lowers intrinsic
height, and an equal-coefficient smaller source contradicts the tie choice.
Therefore every prefix of S* has no LEX improvement.

For a fixed prefix, H=Y_L(S*)<h0 strictly: there are infinitely many future
odd inputs, hence further positive normalization increments. For each of
the finitely many z<H, eventual periodicity forces a coefficient crossing,
while nonperiodicity gives Y_k(z)->Ycal(z)>=h0>H and a finite normalization
cut. Consequently the **unlimited** safe-root procedure terminates and a
P283 certificate exists for each fixed prefix of S*. This extends P259's
strict-gain conclusion to LEX and the new cover; it does not prove that such
S* is absent or prove general-input termination.

There is also a non-effective uniform finite-core description. Height values
are locally finite: Ycal(n)<=R implies n<R. Choose a rational R>h0 so close
that there are no height values in (h0,R]. For every positive z<R outside M,
either its future is periodic and it eventually crosses, or Ycal(z)>R and
it eventually crosses the R normalization barrier. The union of these finite
stopping traces is finite and independent of the prefix length of S*.
Every member of M remains safe with Y_k<h0<R. Thus a finite unresolved
set of minimum-height roots is compatible with the hypothetical counterexample.
No effective computation of R,h0,M or of a last cut follows. This is an
existence theorem under an explicitly hypothetical nonempty source set, not
an exhibited counterexample. The least-source tie used here cannot be silently
combined with a greatest-source tie in the same height class.

## 6. NG51 — short hits cannot be dropped

Hypothesis: after making the safe-root cover, testing only depth-N surviving
roots and their complete histories suffices; crossing leaves need no earlier
hit checks. It is false even for an empty target. At S=y=14, gamma=1, b=13,
N=4, the source 9 reaches 14 with word 1 and coefficient 3/2. Its next step
is even: 9 --10--> 7 has coefficient 3/4 and becomes a crossing leaf before
depth N. No depth-N survivor supplies the missed safe improvement. Literal
enumeration through each first crossing proves minimality in S among empty
positive targets: all S<14 have no such false negative. This is not minimality
over all nonempty targets or certificate languages.

The supplied blind-cover S=17 example is retained: 11 --1-->17 is hidden
if grouped under its later crossing word 11010 and only leaf endpoints are
checked. That broader faulty checker also ignores earlier hits of traces;
S=17 is not the new minimality statement. An early local hypothesis that
S=11 worked confused the literal bits of 7 with 1100; independent iteration
rejected it (7 actually begins 1110). It was corrected before acceptance.

Failure is local to the proposed pruning rule, not to safe-root certification.
The weaker surviving rule is P283 with every short prefix checked. A second
mandatory boundary is the supplied q22 lifted equal-coefficient pair: at an
even state Y=H a smaller source must continue, since the next even step can
complete a LEX improvement. This is verified exactly by the boundary tests.

## 7. Finite evidence, independence and unaccepted material

E65 reproduces all five mathematical output components of the supplied
driver and all 185 no-improvement certificates exactly. The new evidence
also stores every one of the 10,240 query witness sets and all 2,483 positive
improvement certificates, so corpus completeness is independently testable.
Extrema: 524287 words through 18, 72 safe (q,L) pairs. The independent
binary recurrence additionally enumerates through 19 (1048575 nodes) to
obtain the small-Q oracle's extrema; this auxiliary scope is explicit.
Small literal orbits: 256 sources through 19, 4864 source/length prefixes.
Q caps: 1,2,4,8,12. Thresholds: 1,9/8,3/2,27/16,2,9/4,3,4.
There are 16865 decoder candidates and 2744 safe witness occurrences, not
2744 distinct sources. Some queries have zero candidates.

All-length targets: S=1..127,L=0..20 plus (703,80); 185 no-improvement,
2483 improvement. Independent sources 1..705 are followed to their first
repeat, with 1189 distinct states and contracting return coefficients. This
is a complete reference for the finite target set's bounded source pools,
not a finite-depth assertion about unknown large sources. Certificates use
unbounded-length cut proofs independently of this reference. At (703,80):
bound 705, N=10, 181 vertices, 91 leaves, 44 roots, 1156 trace steps; 43 roots
cross and one reaches the normalization barrier.

Regressions include 72 mandatory family words, q22 equal/negative-carry
witnesses, NG43's valley 151044095, NG45 formal evidence and both NG46
potentials. Big-integer checks include 2^p+7 at p=80,256,1024 with nonzero
hits, in addition to all-ones controls that can have no candidates. No
historical artifact is rewritten. Existing Phase 41 and Phase 43 interfaces
are unchanged; this supplement is a separate search/certificate mode.

The supplied generator/reference code was audited and adapted; independent
reconstruction is not independent authorship. The standalone evidence
verifier imports neither search implementation. It uses literal iteration
instead of the window decoder, binary recursion instead of position-mask
enumeration, and first-return comparison instead of safe-tree pruning.
Both checkers use explicit exceptions and retain rejection under `python -O`.
A proposed tamper test that shortened (703,80) to (703,79) was corrected:
the last even step permits a genuinely valid reused certificate, so rejection
was not mathematically warranted. Corpus query identity is checked separately.

B1 is accepted only as P281/P282 with their stated domains. Backlog B2--B6
remains unreviewed. The ZIP's 31-ratio exploratory dyadic graph output was
read but is not independently accepted or needed here; no general stateful
or all-ratio impossibility is inferred, and it is not stored as accepted
evidence. Its source hash is retained in [provenance](PROVENANCE.md).

## What this result does not prove

No successful-ancestor lower bound, universal termination, effective final
join/cut, empty minimum set, infinite ordinary source, H112/H72/H89 solution,
positive-cycle exclusion or Collatz proof is supplied. The new bottleneck
remains forcing an actual LEX improvement from one fixed ordinary source's
carry/lifts/ancestry, or contradicting compatible certificates at that source.
More finite windows or a smaller initial tree alone cannot do this.
