# Transient sparsity and finite normalization — independent audit

Date: 2026-09-10. Base: `feb29b423d43445f1c7d826d6ef71a25e2854b44`.
This is an unnumbered supplement to Phase 44, not a duplicate new phase.
`proves_collatz=false`. H112/H72/H89/H133 remain `OPEN`.

## 1. Provenance, claims and exact domain

The supplied `collatz_transient_sparsity_20260910_bundle.zip` has SHA-256
`0f3811f9274e5cf605ddd3f66e0f935a0ad28c9e97aec4a0c3835401b5763eda`.
All eight member hashes were checked. Its notes and three Python programs
were read before execution. The proposal started at Phase 43; current main
already contains its F1/F2 as P267. We reuse P267 without a duplicate claim.
The generator and verifier are audited adaptations of the supplied programs,
not independent authorship. Their arithmetic reconstructions are different.
No external theorem or new literature-novelty claim is needed here.

| ID | Status | Accepted scope |
|---|---|---|
| P267 | VERIFIED_THEOREM, unchanged | Terminal-loss finite-trajectory sparsity, already Phase 44. |
| P269 | VERIFIED_THEOREM | Transient recursive capacities and the finite-capacity/actual-occupancy tail splice below. |
| P270 | VERIFIED_THEOREM | Uniform finite normalization, source-floor refinement and finite predecessor corollaries, using E62. |
| E62 | VERIFIED_FINITE | Exact finite tables, affine enumeration, orbit windows, controls and independent reconstruction. |
| NG48 | REFUTED | Removing distinct-input hypotheses from the uniform 256 normalization bound. |

Use the full shortcut map `T(x)=x/2` on even integers and `(3x+1)/2`
on odd integers. Bits are input parities in chronological order.
Let `x_i=T^i(S)`, `S` a positive ordinary integer, and `M>=0` an integer.
Require the **input** states `x_0,...,x_(M-1)` to be pairwise distinct.
The closing endpoint `x_M` may repeat an input. Empty paths are permitted.
For the empty word, L=q=B=0, its map is the identity and its canonical
residue modulo `2^0=1` is 0. For q=0 any word is all-even with B=0.
Nothing is assumed about nonperiodicity of the future, coefficient safety,
or a computational Collatz exclusion threshold. Windows `[a,a+X)` have
integer `a` and integer length `X>=1`; only positive states are counted.
Negative anchors reduce to the positive-domain bound by containment.

## 2. Terminal restriction and P267 reuse

For selected indices `I={i<M:x_i in [a,a+X)}`, retain only `i+N<M`.
At most `N` indices are lost **in total**, not once per weight class.
Their images `x_(i+N)` are distinct and belong to the same finite path.
For `N=0` nothing is lost; for `M<=N` the retained set is empty.
No injectivity beyond the closing endpoint has been assumed.

The complete distinct orbit set of `2^m` is `2^m,...,2,1`; for
`1<=N<=m-1`, its full `T^N` image loses exactly `N` points. Thus terminal
loss cannot be removed by pretending every eventually cyclic orbit is
equal-time collision-free.

P267 (the [Phase 44 proof, Section 6](../edit-capacity/REPORT.md)) already
establishes, uniformly in all such paths and windows,

    # {i<M:x_i in [a,a+X)} < 32 X^(29/30).                 (2.1)

Its induction uses `N=ceil(log_2 X)`, `theta=14/23`, low-weight recursive
terms, a high-weight binomial tail, and the single extra `N`. The supplied
power comparisons at `N=135` and their persistence are independently
reconstructed by E62. Small `N<135` is covered by `X<=2^134<32^30`.
We do not count this as a new independent proof of P267. The same
finite-prefix argument covers the set of distinct values of any complete
positive orbit, including the prefix up to its first repeat; it never
bounds visit multiplicities on a cycle.

## 3. P269: transient recursive capacities

For a length-`N`, weight-`s` word its affine map is
`(3^s x+B)/2^N`. Moving any one to the right across a zero increases B;
thus the extremal words are `1^s0^(N-s)` and `0^(N-s)1^s`, giving

    B_min=3^s-2^s,  B_max=2^(N-s)(3^s-2^s).

Every word has one canonical residue modulo `2^N`, so a window of width
`2^N` contains at most one source for that word. For a width `X` window,
the weight-s images lie in at most

    Y_Ns(X)=1+floor((3^s(X-1)+(2^(N-s)-1)(3^s-2^s))/2^N)

consecutive integer slots. Write `m_Ns=ceil(log_2 Y_Ns(2^N))`; this is
computed by `(Y-1).bit_length()`, with `m=0` when `Y=1`.

Define `At_0=Ot_0=1`, and for every integer `N>=1`,

    At_N=min(2^N, N+sum_(s=0..N) C_Ns),
    C_Ns=min(binomial(N,s),At_m) if m=m_Ns<N,
         =binomial(N,s) otherwise;
    Ot_N=min(2^(N-1), N+sum_(s=1..N) Codd_Ns),
    Codd_Ns=min(binomial(N-1,s-1),At_m) if m=m_Ns<N,
            =binomial(N-1,s-1) otherwise.                (3.1)

Induct on N. After deleting the last at most N selected inputs, each
weight-class image lies in a window of width at most `2^m` in the **same**
finite path, so the smaller general capacity `At_m` applies. The source
word bound gives the binomial alternative. For odd selected inputs the
first bit must be one, but their images need not be odd; hence use `At_m`,
never `Ot_m`. Add the single shared loss, then the trivial integer/odd
occupancy cap. This proves (3.1) bounds every allowed finite path.
The old P228 arrays `A_N,O_N` are different and remain unchanged.

| N | At_N | Ot_N |
|---|---:|---:|
| 10 | 797 | 512 |
| 20 | 455424 | 326376 |
| 30 | 267290382 | 196173532 |
| 40 | 185533512221 | 130670392473 |
| 48 | 31389538711236 | 24049168702207 |
| 49 | 58609949691167 | 42931386607713 |
| 50 | 114046777568200 | 86887477037540 |

### Essential correction: actual occupancy is not a raw upper-bound table

Let `c_N(P)` be the number of odd inputs in `[2^N,2^(N+1))`.
We know separately `c_N<=Ot_N` and `c_N<32*2^(29N/30)`.
These inequalities do **not** imply `Ot_N<32*2^(29N/30)`.
The proposal used precisely that unjustified inference. The raw-table
inequality is unestablished here, not disproved; it is unnecessary.

For `N<=500` use the computed `Ot_N`; for `N>=501` use (2.1) directly
on `c_N`. Since `2*44^30>45^30`, the true occupancy tail satisfies

    sum_(N>=501) c_N/2^N < eta :=1440(44/45)^501.

Consequently for `b<=500` and every allowed finite path,

    sum_(odd inputs x>=2^b) 1/x
       <=sum_(N>=b) c_N/2^N
       < F_b :=sum_(N=b..500) Ot_N/2^N +eta.             (3.2)

The same notation problem was present in Phase 38 Section 5 and the
Phase 43 Section 5 citation. Their text is corrected to actual `c_N`
for the infinite sum, using the old arrays only through 500. Their
conclusions P229/P260, statuses and historical artifacts are unchanged.
No all-scale bound on the raw recursive arrays is needed by those proofs.

## 4. P270: finite normalization with no future hypothesis

E62 reconstructs the rational certificates

    F49 <2079/1000,
    F19 <15/2,
    R :=sum_(odd 1<=x<32)1/x + F5 <82/5.                (4.1)

The first three positive terms of the atanh expansion give
`log 2 >842/1215`. Also `log(13/8)>10/21`, hence
`log 13 >3*842/1215+10/21 >5/2`. Exact rational comparisons show
`2079/1000<3*(842/1215)` and `82/5<24*(842/1215)`.
All numerical proof decisions use integers or rationals, not floating point.

Let `q_j` count odd inputs before time j. For every `0<=j<=M`,

    Y_j=2^j x_j/3^q_j
       =S product_(i<j, x_i odd)(1+1/(3x_i)).           (4.2)

This identity follows from multiplying each literal transition, not from
asymptotics. As `log(1+u)<u` for u>0, (3.2)--(4.1) imply:

* always `S<=Y_j<256S`;
* if every input before j is at least `2^19`, `Y_j<13S`;
* if every input before j is at least `2^49`, `Y_j<2S`.

For an empty or all-even prefix the ratio is 1 directly; this also handles
vacuous source-floor hypotheses. These are not statements about arbitrary
paths with repeated inputs. Their proofs use neither X02 nor E46 nor a
nonperiodic-future assumption. The smaller old tables still give valid
stronger special-purpose bounds on their original domain.

For a non-dropping allowed path, all inputs are at least S. Apply (2.1)
to shells `[2^k S,2^(k+1)S)` to obtain, with `r=2^(-1/30)`,

    log(Y_j/S) <=32/(3(1-r)) S^(-1/30) <480 S^(-1/30).

Thus `Y_j/S=1+O(S^(-1/30))` as positive integer `S->infinity`, with an
absolute constant uniform in finite j satisfying the distinct-input and
non-dropping hypotheses. This is a uniform-length bound, not a length cap.

## 5. Finite maximality, source pools and K

Suppose a finite positive literal path has maximal coefficient among
**all** positive integer sources and all lengths/odd counts leading to
its endpoint. By concatenating a common suffix (P261), each prefix is
also maximal. Its nonempty coefficient is strictly greater than one:
the empty path is a competitor of coefficient one, and `3^q=2^L` is
impossible for positive L. The affine constant is nonnegative, so every
nonempty prefix strictly exceeds the starting state; in particular it is
dropping-safe.

It cannot repeat a state, including at the closing endpoint. A positive
literal cycle fixes `x>0` with `(3^q x+B)/2^L=x` and `B>0`, so its
coefficient `1-B/(2^L x)` lies strictly between zero and one. Deleting
that loop retains a positive literal path and strictly increases its
coefficient. This contradicts maximality. None of this implies monotone
odd defects: both NG46 certificates `(7,4)` and `(703,80)` are rechecked.

For **any distinct-input** target prefix of source S, endpoint y and
coefficient c, P257 gives `z<y/c=Y_j` for every strictly better positive
competitor, including empty/even/unsafe/different-Q competitors. Thus
`z<256S`; if it is non-dropping with `S>=2^19`, `z<13S`.
This bounds a search's source pool, not its join time or successful search.

For a target with repeated inputs, loop deletion gives **one** improving
witness starting at S. It does not bound **all** competitors by 256S.
Conflating these two assertions would incorrectly extend the theorem.

The finite height padding condition `2^K>=3Y_j` is guaranteed by
`K=ceil(log_2 S)+10` for distinct targets, and by
`K=ceil(log_2 S)+6` for non-dropping targets with `S>=2^19`.
Indeed `1024>3*256` and `64>3*13`. These constants only supply padding;
they prove no domination, ancestry, carry closure or H112 exclusion.

## 6. E62, falsifiers and independence

The generator uses binomial closed forms, positional affine constants and
prefix weight differences. The verifier uses Pascal rows with dynamic
affine extrema, exhaustive literal positive residue enumeration, and
direct T^N image tracking. It reconstructs all 501 rows, 32767 words and
25020 declared windows; 15420 windows have a nonzero terminal deletion.
Core capacity/constant/affine/window components match the supplied JSON
exactly; accepted metadata and explicit scope safeguards are new.

Additional evidence includes 48 words from `(110|111)^*`, A=11101,
B=1100 and A^r B^s; 28 actual normalization paths including `2^m-1`,
`8^m-5`, empty/closing-repeat cases and nonvacuous high-floor examples;
all source-1 prefixes through 40; and preserved historical hashes.
The verifier rechecks the two NG46 all-length potentials arithmetically.
Tests check every subset of abstract paths `M<=10,N<=12` (26611 cases),
nonpositive window anchors, domain rejection and scope tampering.

NG48: for S=1 the orbit is `1,2,1,2,...`, and
`Y_L/S=(4/3)^ceil(L/2)`. Since `(4/3)^19<256<(4/3)^20`, the first failure
at **this source** is L=39. S=1 is the least positive source. The supplied
L=40 witness is retained; no global length minimality over other sources
is claimed. Distinctness is a fundamental hypothesis, not a floating-point
or small-size anomaly. The negative fixed point -1 has expanding
coefficient 3/2 and is outside positive-cycle contraction.

NG22/NG45 formal words and the EXT08 prescribed-real examples are outside
the positive-ordinary finite-path inference unless literally realized at
each stated finite prefix. Their existing countermodels are not discarded
or converted into ordinary infinite trajectories. The new proof makes no
new universal claim about those formal languages.

## 7. What this result does not prove

This proves neither Collatz nor H112/H72 nor positive-cycle exclusion.
Finite normalization does not construct an improving ancestor, give an
effective last join, establish monotone defects, or upgrade finite source
residues to an infinite ordinary source. It does not bound repeated visits,
raw recursive capacities at arbitrary scales, or all predecessor sources
of a repeated target by 256S. Infinite proofs here are written mathematical
audits, not machine-formalized proofs. Exact tables and tests certify only
their declared finite arithmetic and implementation scope.

Next work should couple the now explicit finite source pool to literal
carry, cross-source ancestry, or an effective incompatibility of all-prefix
maximal certificates. Merely extending table depth or repackaging sparsity
does not supply that missing mechanism.
