# Synchronized shadow closure — independent audit

Date: 2026-09-11. Base main: `12df6b8781957923d8069293f4ad2c0e13c0f7bd`.
Unnumbered supplement; latest numbered phase remains 44.
`proves_collatz=false`; H112/H72/H89/H133 and EXT08 remain `OPEN`.

## 1. Decision and authority

Accept the supplied S1--S8 with the explicit domains below. No fatal
mathematical error was found. The new finite checks strengthen, rather than
replace, the analytic reductions. New IDs are P274--P280, E64 and NG50.
The [archived proposal](PROPOSAL.md) is provenance, not a second authority.
[The backlog](../../notes/UNINTEGRATED_THEORY_2026_09_11.md) retains B1--B6
as OPEN, unreviewed research; none is certified by these graphs.

ZIP SHA-256:
`6b276556e66271daddae1077d9ca7bdc06a421e0414004b71a319e647ab519e2`.
All ten supplied member hashes matched. Supplied proof, instructions,
backlog, generator, verifier, tests and execution records were read in full;
all seven mathematical evidence components were independently reconstructed.
The supplied implementations were audited and adapted. Different algorithms
are logical independence, not independent authorship, external peer review
or proof-assistant formalization. All decision arithmetic is integer/rational.

## 2. Conventions and reused facts

Use input parity in chronological order for shortcut T(x)=x/2 if even,
(3x+1)/2 if odd. Write F_w(x)=(A x+B_w)/M, A=3^q, M=2^L,
and F_uv=F_v composed with F_u. If the ones occupy p_0<...<p_(q-1),

    B_w=sum_j 2^p_j 3^(q-1-j).

For fixed L,q,B, valuation stripping recovers every p_j uniquely: the
lowest power of two in the remaining sum comes only from its first term.
Alternatively, the final integer condition selects one residue modulo M;
induction modulo 2 recovers the entire literal branch sequence. Thus a
positive integer input with integer final affine output follows that word,
with positive intermediate states. This does not imply coefficient safety.
The coordinate bounds j<=p_j<=L-q+j give

    B_min=3^q-2^q, B_max=2^(L-q)(3^q-2^q).

These facts reuse P125/P219/P248, not new general decoder claims.
Safety means 3^(prefix weight)>2^(prefix length) at every nonempty prefix.
Irrationality of log_2 3 removes nonempty equality. A safe word of q>=2
starts 11, and its ones satisfy p_j<=f_j=floor(j log_2 3).

For a positive nonperiodic source n, P242 gives the intrinsic height

    Ycal(n)=lim_k 2^k T^k(n)/3^(odd count before k)>n,
    Ycal(T^L(n))=(3^q/2^L)Ycal(n).

For the finite expanding block alphabets here, convergence can also be
proved directly: at boundary j, x_j/C_j=n+sum_(t<j)(B_t/M_t)/C_(t+1).
Uniformly bounded corrections and min c_i>1 give a convergent geometric
majorant. Intermediate normalizations lie between successive boundaries.
No EXT08, X02 or random-parity hypothesis is needed.

## 3. P274 — minimum equal-coefficient collision and finite valuation resource

The two words

    d=1101101101011011011010110110101101
    a=1111111111011100011111001100001100

are safe, L=34,q=22, B_d=165490842749, B_a=39966604313,
B_d-B_a=4*3^22. Their least positive sources are 7435082747 and
7435082751, with common endpoint 13581056558. Every nonnegative lift by
2^34 preserves this collision. Equal coefficient is not a strict gain.

Minimality is in q only, among distinct positive literal safe sources
coalescing with identical L and q. For q>=2 both sources are 3 mod4,
so a nonzero correction difference is at least 4*3^q. The maximum safe
correction is at most Bsafe(q)=sum_j 2^f_j 3^(q-1-j); its minimum is
3^q-2^q. Twenty exact comparisons exclude q=1..20 (q=1 only has word 1;
q=0 has only the empty safe word and cannot give distinct coalescent sources).

For q=21, P=10460353203, the larger correction must be at least
5P-2^21. Its allowance below Bsafe is 1720560640<P/6. Moving position
j>=1 left loses at least 2^(f_j-1)3^(20-j)>P/12, since 2^f_j>3^j/2.
Position zero cannot move; two moved positions already exceed the allowance.
With one moved position and unchanged predecessor, only a gap of two can
shrink by one. The complete choices are none or

    j=2,4,6,7,9,11,12,14,16,18,19.

The final position stays 31 and the only safe lengths are 32,33. The width
is <8P, excluding larger source gaps. All 24 candidates B-4P fail the
valuation decoder. This is a complete remainder, not a depth extrapolation.
P256 concerns a shorter alternative and negative carry, and remains distinct.

Prefixing d/a by u1^r/v1^r (blocks in Section 4) gives collisions at every
r>=0, with length 11r+34 and q=7r+22. The difference stays four.
Canonical residues do not wrap: the small-source word starts 110, so its
residue is 3 mod8 and at most 2^L-5. For terminal d-source x,
v2(139x+2903)=5 for the entire residue class modulo 2^34. Each u1 block
multiplies Z=139x+2903 by 2187/2048. Consequently

    v2(139S+2903)=11r+5,
    S>=(2^(11r+5)-2903)/139.

Different r families are disjoint, not a claim of pairwise coprimality.
Choose a lift S=1 mod3; z=(2S+7)/3<S is positive, odd, and T(z)=S+4.
The path 1 v1^r a coalesces with u1^r d and has coefficient 3/2 times
the target. This constructs arbitrary-depth families at different sources,
not arbitrary-depth improvements at one fixed integer.

## 4. P275 — four-block peers and a smaller different future

The following exact data fix the left/right alphabet (labels here are 1-based;
JSON labels are 0-based):

| i | u_i | v_i | L,q | B_u,B_v | least u source |
|---|---|---|---|---|---:|
| 1 | 11011111000 | 11111010100 | 11,7 | 2903,2347 | 539 |
| 2 | 11011011111000 | 11111111000100 | 14,9 | 34159,20963 | 2299 |
| 3 | 11011110011010 | 11111011010100 | 14,9 | 36751,23555 | 411 |
| 4 | 11011110101010 | 11111011110000 | 14,9 | 34447,21251 | 9371 |

All eight words are safe, and B_v-B_u=4(M-A), hence
F_v(x+4)=F_u(x)+4. **If** a positive integer S realizes any infinite
left schedule, S+4 realizes the matching right schedule. Boundaries diverge
at least geometrically, so both literal orbits are nonperiodic. Their
normalized heights agree because the normalized difference is 4/C_j ->0.
This conditional construction does not establish that such S exists.

For the first left endpoint y, the next block enforces oddness. Its last
odd position also gives y=1 mod3, so z=(2y+7)/3 is positive odd and
T(z)=y+4. The exact condition 6z<5S is 4y+14<5S. Substitution gives
the four thresholds 27,91503/797,94095/797,91791/797, each strictly below
the corresponding least source. Therefore every such source has

    z<5S/6, Ycal(z)=(2/3)c_i Ycal(S)<=6561/8192 Ycal(S)<Ycal(S).

No global minimum ordinary nonperiodic source, or global height-minimizing
nonperiodic source, can lie in this particular left language. However the
new source's language need not return to it: no iterative descent closure.

These two original futures do not coalesce even at unequal times. For
fixed h>=1, |T^h(x)-x|<=4 implies x<=3^h+3*2^h: use the affine equation,
|3^q-2^h|>=1, and B<=3^h-2^h (the all-ones global maximum). A time-shift
coalescence would give this inequality at arbitrarily large paired boundary
values, a contradiction. Equal-time coalescence contradicts difference four.
Thus z shares the right future, not the left one. It is not automatically
an ancestor of the original source or in its shared-future class.

## 5. P276 — bounded offsets and all synchronized same-height peers

For a finite expanding left alphabet and arbitrary right words with the same
L_i,q_i in each block, put d_j=b R_j-p S_j for fixed positive integers p,b.
Then d'=(A_i d+b B'_i-p B_i)/M_i. Set

    D_-=min_i (p B_i-b Bmax_i)/(A_i-M_i),
    D_+=max_i (p B_i-b Bmin_i)/(A_i-M_i).

If b Ycal(R)=p Ycal(S), every d_j lies in [D_-,D_+]. Indeed, above D_+,
d'-D_+>=c_i(d-D_+); division by the future coefficient product leaves
a positive lower limit, contradicting height equality. Below D_- the
opposite inequality gives the same contradiction. This proves boundedness
from the limiting ratio, not as an extra assumption. Conversely bounded
offsets imply the limiting ratio, since C_j diverges.

For p=b=1 these bounds are -30041/139 and 844/139: exactly 223 integers
-216..6. Each of the 892 state/label pairs determines the right residue
r_u+d modulo 2^L and therefore exactly one literal word. Keeping the required
q and range yields 122 edges. The independent verifier instead enumerates
all 330 words of (11,7) and all 2002 words of (14,9), and solves their
residue congruences for d. Even and unsafe right words are included.

SCC reverse reachability gives the 15 live states

    -83,-81,-79,-78,-77,-76,-74,-69,-68,-64,-20,-18,0,3,4.

All negative live states reach a single-label self-loop within at most
three transitions: -83 uses label 4, -20 label 1. The verifier additionally
checks a decreasing rank on the remaining negative edges and absence of
loop exits. A positive integer cannot eventually repeat an expanding word
forever: Z=(A-M)x+B>0 changes to (A/M)Z, consuming exactly L powers of two
per block. This finite integer resource excludes all negative live states.

The remaining edges are 0->0 and 4->4 for every label, plus 3->4 only
for label 2. Thus, conditional on an actual infinite left source S, the
entire class of positive same-height peers with **that identical per-block
L/q history** is {S,S+4}, augmented by S+3 exactly when the first label is 2.
The third word is 01111111010100; it is even and unsafe at its start and
joins the right branch after one block. Its half is <S and has height
Ycal(S)/2. The finite control S=15288571 gives endpoints 18367003 and
18367007 for S and S+3 respectively. It is not an infinite realization.

We do not mark an unrestricted positive-infinite two-peer conjecture REFUTED
using only this finite control: the infinite antecedent remains unestablished.
The exact conditional classification includes the third peer without
claiming that its infinite instance exists.

## 6. P277 — no synchronized ratio-2/3 peer for this alphabet

Set p=2,b=3 in Section 5. The bounds are -93026/139 and 15989/3299,
giving 674 integer states -669..4. All 2696 state/label combinations give
334 edges, independently recovered using the same unrestricted right pool.
The 13 live states are -174,-170,-168,-167,-164,-163,-162,-160,-159,
-157,-149,-41,-37. They reach the label-4 loop at -167 or label-1 loop at
-41 within one step. The same valuation argument excludes them for an
actual infinite positive left source. Hence no positive synchronized peer
of intrinsic height (2/3)Ycal(S) exists under this left-schedule hypothesis.

The initial condition **3 divides 2S+d** is necessary for R=(2S+d)/3.
The graph deliberately overapproximates by dropping it; exclusion of the
larger graph's positive realizations is sound. For each retained edge we
also check three consecutive dyadic source lifts: exactly one meets the
mod3 condition. All 334 resulting actual finite transitions are rebuilt.
This does not promote every graph path to a positive infinite trajectory.
The different-time construction in Section 4 is outside this synchronization,
as are the other ratios in Section 7.

## 7. P278 — literal contractions on two-block subalphabets

For H(x)=(p x+d)/b, the conjugacy equation at equal L/q is
B_v=(p B_u+(M-A)d)/b. The complete claimed instances are

| input labels | H | output words |
|---|---|---|
| 2,3 | (x-95)/4 | 11101100001111; 11110010001111 |
| 3,4 | (x-83)/8 | 10111110101010; 10111011111000 |
| 3,4 | (3x-241)/32 | 11111010101010; 11101111100010 |

At each left boundary the next block supplies S=3 mod4 or S=27 mod32,
as required. The least sources above exceed 95,83,241/3; expanding positive
blocks preserve those lower bounds. H(S) is therefore positive integral and
strictly smaller, at every boundary. The identity plus final integrality
proves literal right words. Normalizing gives Ycal(H(S))=(p/b)Ycal(S).
The last formula also follows by T^2 after the (x-83)/8 transform, whose
right words start 10. None of these output alphabets is asserted closed
under iteration of the same transformation, or to contradict Section 8.

## 8. P279 and NG50 — complete three-map affine integer obstruction

Ask for one invertible H(x)=rx+s, 0<r<1, conjugating u2,u3,u4 to arbitrary
Collatz words, and taking at least one integer input to an integer output.
Equality of slopes forces every output to L=14,q=9 by unique factorization;
there is no unproved length cap. With D=3^9-2^14=3299 and left corrections
34159,36751,34447, the output corrections must be

    K, K+9k, K+k; k=288r in {1,...,287},
    s=(k*34159-288K)/(288*3299).

All real r,s are covered: rationality follows from integer correction
differences, not an initial restriction. If H(x)=z with x,z integral,
3299 divides k*34159-288K. Enumerating the full 2002-correction pool gives
1179 candidate pairs (k,K), and each of their 3299 residues is nonzero.
The generator scans 574574 scale/correction pairs; the verifier enumerates
nearby ordered corrections and checks the third member separately. Every
candidate and residue is stored; this is a finite certificate of the
impossibility, not merely a bounded search with no hit.

At r=1 the same congruence is sufficient: integer translations are exactly
0 and +4, from K=34159 and 20963. There is no negative common translation.
NG50 records the refuted existence hypothesis on these three specified maps;
no minimum over all possible alphabets is claimed. Real symbolic conjugacies
exist, but all contractions fail the ordinary-integer input/output condition.

This does not exclude state-dependent, time-shifted, different-Q, nonlinear,
occasional pointwise or different-alphabet rewrites. A general impossibility
claim about finite-state rewriting would be an invalid scope promotion.

## 9. P280 — self-closure of a finite expanding affine family

Let a nonempty finite family F of maps a x+b have a>1. If a single
H(x)=rx+s with 0<r<1 satisfies H F H^-1 subset F, conjugation is injective
and hence permutes F. Within each slope its finite intercept set is permuted
by b->rb+(1-a)s. Diameters shrink by r, so each such set is a singleton.
Its fixed equation gives b/(1-a)=s/(1-r), a common fixed point for F.
Conversely, dilations about a common fixed point commute with all maps.

For nonempty Collatz words of coefficient >1, that point is p/d<0 in
lowest terms with odd positive d, because A-M is odd and B>0. For any
positive legal switching orbit Z=dx-p is a positive integer and transforms
as Z'=(A/M)Z. Each block decreases v2(Z) by L. Thus total legal block
length is at most v2(dS-p); there is no positive infinite switching source.

Common-fixed-point affine maps commute. For two corresponding words,
F_uv=F_vu, their slopes force equal counts and their corrections agree;
the decoder proves uv=vu. Removing the shorter word from the longer word
repeatedly proves that both are powers of one primitive word. Applying
this to a fixed member of the family gives one common primitive root.
This concerns one affine self-conjugacy, not arbitrary stateful rewriting.
Finite regression uses every expanding binary word through length six,
three repeated blocks and all equal-center pairs; the theorem is the
all-length algebra above, not those tests.

## 10. Handoff, representative choices and independent evidence

P242's finite height sublevels give a global minimum if nonperiodic sources
exist. Within one equal-height class either a smallest or a largest ordinary
source may be selected, but one cannot silently use both tie-breakers on
the same representative. Section 4's strict height descent needs neither.
Also distinguish a global minimum from a minimum inside one shared-future
class: the different-future reduction does not stay in that class.

E64 reconstructs the declared finite corpus: 2332 distinct right words,
122/334 graph edges, 24 q=21 cases, 1179 affine contractions, 1364 finite
schedules/4092 lifted pairs, 1023 even-third-source checks, 1134 two-letter
contraction pairs and 68 repeat lifts. These are different counting domains.
The 570663 count covers pair/third literal steps only, not every auxiliary
check. Added evidence covers 334 integer-compatible ratio edges, all 20
one-position loss margins, all four shrink thresholds, 48 adversarial words
and 28 finite paths. Six old hashes are pinned; NG45 is rebuilt and both
NG46 potentials reverified. NG43 and common-center controls receive tests.
All old artifacts, including historical status snapshots, remain unchanged.

The proposal's 32 tests were adapted to pytest; an initially exposed dynamic
unittest method caused one collection error and was removed from module scope.
This was a test-integration error, not a failed mathematical claim. Additional
scope, integrality, graph-rank, duplicate-key and optimized-Python tamper
checks were added. Final actual commands/counts/hashes are in the
[run record](../../../SYNCHRONIZED_SHADOW_RUN_RESULTS.md).

Backlog B1--B6 is retained without acceptance: fixed-Q search compression,
critical all-orbit counts, log-power 0.98 improvement, operator reformulation,
approximate fixed points and sourcewise residual constants need separate
proof/quantifier audits. Only arXiv metadata/abstracts were checked for the
three cited papers; no external theorem is a premise and no literature-wide
novelty claim is made. See [LITERATURE.md](../../../docs/LITERATURE.md).

## What this result does not prove

No infinite positive ordinary source for the four-block language is
constructed or excluded in general. A global minimizer is excluded from
that specific language, not from the full safe language. Synchronized peer
classification is not all-ancestor classification. Real affine identities
are not integer-source maps. A smaller different future is not necessarily
coalescence or a closed descent. Arbitrarily deep lifted families need not
apply to one fixed integer. P272's mass bound is not contradicted by a
bounded supply of two or three peers. Positive-cycle exclusion stays separate.

The next missing theorem is a complete source/lift-linked transformation
allowing state dependence and time/Q differences, with a closed image
language or an independently decreasing rank for the nonclosed remainder.
No such existence/coverage theorem is supplied; H112/H72/H89/H133 stay OPEN.
