# EXT08 scope audit — prescribed real branches are not literal parity orbits

Audit date: 2026-09-10. Base: `2da31e63c87f7c2225899f2d2c500629a0e5668d`.
This is a correction audit, not a new numbered search phase.
Current EXT08 status: `OPEN`; theorem statement **not** `REFUTED`.
`proves_collatz=false`.

## 1. Source and exact scope of the objection

Primary source: Josefina López and Peter Stoll, *The 3x+1 Periodicity
Conjeture in R* (2021), [arXiv:2101.12747v1](https://arxiv.org/abs/2101.12747v1),
[original PDF](https://arxiv.org/pdf/2101.12747v1). This is the arXiv preprint;
no journal publication is asserted here. The downloaded PDF SHA-256 is
`e4c5bccec262d8fdb001d7970dee56c347c03d789796c165e79a18dc2d584b9a`.

Complete printed pages 4, 7, 8, 28, 29 and 30 were visually reviewed, as well
as searchable text. Page 4's Scheme 2 identifies prescribed real dynamics
with literal parity dynamics when the real limit is in Q_odd. Pages 7–8,
(15)–(16), transfer properties of the real limit to its coherent residue
sequence. Lemma 24 on page 28 asserts distinctness of the real trajectory.
Theorem 1's upper-density argument on page 29 uses Lemma 26 and this
real/2-adic transfer; page 30 completes the lower-limiting-density conclusion.
The countermodels below target those auxiliary steps, not the rational
2-adic theorem statement. No missing parity-consistency hypothesis appears
in the inspected statements. [Source](https://arxiv.org/pdf/2101.12747v1).

The arXiv record displayed only v1 at the audit date. Targeted searches for
the identifier/title with `correction`, `erratum`, and the authors/density
terms did not locate a repaired or independent proof. This bounded search
does not establish that no repair exists. The authors' 2009 Sturmian paper
concerns a narrower word class, not a verified repair of the universal claim.
No literature-wide novelty or specialist endorsement is asserted.

## 2. Convention and common identity — P268

For a prescribed bit, define real affine maps

    f_1(x)=(3x+1)/2,  f_0(x)=x/2.

They are defined for every real x, regardless of its parity. By contrast,
literal shortcut T selects the bit x mod 2 on integers or Q_odd. A prescribed
trajectory leaving Q_odd is not an actual trajectory there.

Write N for prefix length, q_N for its number of ones, d_j for the position
of its j-th one (j starts at zero), and

    c_N=3^q_N/2^N,
    B_0=0, B_(N+1)=3B_N+2^N on a one, B_(N+1)=B_N on a zero,
    P_N=-B_N/3^q_N=-sum_{j<q_N} 2^d_j/3^(j+1).

Induction gives x_N=c_N x_0+B_N/2^N and

    P_N=x_0-x_N/c_N.                                      (A)

Thus bounded negative x_N and c_N tending to infinity imply P_N -> x_0 in R.
Independently, the same positional series converges in Z_2, since d_j tends
to infinity. Its canonical residue modulo 2^N is

    r_N=[-B_N (3^q_N)^(-1)]_(2^N).

These residues lift coherently and have the prescribed first N literal bits:
given a residue/end state at length N, adding 2^N to the source changes that
end state by the odd number 3^q_N, so exactly one lift has the next bit.
This also proves uniqueness of the 2-adic source, without any identification
of its real and 2-adic limits. Every nonempty word here starts in one, so
r_N is positive and odd. Its finite literal realization proves no ordinary
infinite-source stabilization.

## 3. Three exact constructions

Put x=-1-u. The unforced rule is

    if 0<u<1: choose bit 1, u'=3u/2;
    if u>1:   choose bit 0, u'=(u-1)/2.

The equality u=1 is addressed explicitly below, not left to numerical rounding.

| model | initial u | forced prefix | real limit |
|---|---:|---|---:|
| A | 1/2 | empty | -3/2 |
| B | 1 | 1 | -2 |
| C | 4 | (110)^12 followed by 0 | -5 |

In A write u_N=A_N/2^(N+1). Its numerator starts at 1 and changes to 3A_N
or A_N-2^(N+1). It remains positive odd, so u=1 never occurs. Induction
gives 0<u_N<3/2 and exact reduced denominator 2^(N+1) for x_N.

In B the forced one gives u_1=3/2. Thereafter 0<u_N<=3/2, with equality only
initially; reduced denominators of x_N are exactly 2^N for N>=1. The same
odd-numerator induction proves this and excludes u=1 after the forced step.
The first prescribed bit is 1 at x_0=-2, whose literal parity is 0.

In C the literal cycle (-5,-7,-10) executes twelve times. The extra zero
at time 36 is deliberately **not** the literal bit of -5. It sends x to
-5/2, u=3/2; the rule then applies. For N>=37 the reduced denominator is
2^(N-36). All states belong to [-10,-1); the controlled tail is in [-5/2,-1).
Both x_0=x_3=-5 and x_3=x_6=-5 hold, so even a restriction to nonempty
prefixes does not remove the repetition witness.

After any controlled zero, u<=1/4. Three following ones leave u<=27/32<1;
there must therefore be at least four ones between controlled zeros.
There are infinitely many zeros: eventual all-ones would make u unbounded.
Counting the initial exceptions, for every N>=0 we obtain respectively

    5q_N>=4N-3,  5q_N>=4N-3,  5q_N>=4N-32.                (B)

For C, through length 36 the largest deficit 4N-5q is 24, the extra zero
gives 28, and the next zero gives 32. Every later group of at least four
ones and one zero does not increase that deficit. A starts with 110 and
has deficit at most 2 there; B has deficit 3 after its initial 10.
Intermediate ones decrease the deficit and zeros only occur at group ends.

In all models liminf q_N/N>=4/5>log(2)/log(3), using exactly 3^4>2^5.
For deficit b in (B), c_N^5>=3^(-b)(81/32)^N, so c_N grows exponentially.
Identity (A) proves the stated real limits, with error
0<P_N-x_0<=5/(2c_N) in A/B and <=10/c_N in C. Equality in these error bounds
is harmless; no floating comparison or finite limit extrapolation is used.

All words are not eventually periodic. Otherwise an eventual period of
length d and weight m has m/d>=4/5 and affine multiplier lambda=3^m/2^d>1.
Its bounded real iterates must equal its unique fixed point at every period
boundary (subtract the fixed point and iterate lambda). But after the
finite exceptional prefix the reduced denominators strictly increase at
every step. This is a contradiction.

A and C are permanently coefficient-safe at every nonempty prefix. In A,
110 has minimum terminal multiplier 9/8; every later zero-to-zero group
is 1^r0, r>=4, of multiplier at least 81/32. Inside a group the multiplier
first increases. For C, all initial cycle prefixes are safe, and the two
zeros after the cycle repetitions have minimum multiplier (9/8)^12/4>1.
The subsequent groups are as above. Exactly 9^11<4*8^11 and 9^12>4*8^12:
12 is the least buffer in this specified escape family, not a global
minimum counterexample. **B is not permanently safe:** its prefix 10 has
multiplier 3/4. No safety premise is needed for its real/parity mismatch.

## 4. Refuted auxiliary mechanisms — NG47

1. A real limit of this canonical inverse series need not belong to Q_odd
   or be irrational: A has limit -3/2, outside Z_2.
2. Even a real limit in Q_odd need not be the 2-adic source: B has real
   limit -2, but its 2-adic source is odd. The wrong branch is at time zero.
3. An aperiodic real prescribed trajectory can repeat: C repeats -5 before
   escaping the literal negative cycle. This directly defeats the stated
   distinctness assertion when trajectory is interpreted as Scheme 2.
   If interpreted as literal T instead, the real trajectory never escapes
   and is not the sequence prescribed by the aperiodic word.
4. For every r>=12, the C construction with r cycle repetitions has the
   same real limit -5 and is aperiodic and permanently safe. At time 3r,
   this word chooses zero, whereas the construction with more repetitions
   chooses one. Hence these are distinct words: real Phi is noninjective
   even on this permanently safe aperiodic subclass.

The failure is a change of completion, not a failure of coherent residues.
Equation (16) interpreted as the Z_2 limit of partial sums is valid.
Calling that coherent sequence a representation of the *real limit* does
not make the real value its ordinary rational embedding in Q_2. In particular
all rationals embed in Q_2; even-denominator rationals simply lie outside Z_2.
Neither different completion limits nor real rationality decides rationality
of the 2-adic limit. That rationality remains OPEN for these examples.

## 5. Dependency repair, not blanket retraction

EXT08 changes from EXTERNAL_THEOREM to OPEN: the recorded external assertion
has a disputed proof route and must not be an unconditional premise. This
does **not** assert its negation. P119/P121/P123/P124/P128 retain their
CONDITIONAL statements, now explicitly conditional on the unestablished
EXT08. Their implication algebra survives. For positive ordinary
nonperiodic orbits P123/P124's complexity conclusions already follow from
the stronger internal P127, whose proof uses P125/P126 and pigeonhole,
not EXT08. No duplicate theorem ID is needed for that route.

The generated dependency-index closure at the baseline is
EXT08, P119, P121, P123, P124, P128, H72. H72 is a research target containing
context dependencies, not an accepted theorem depending on all of them.
H112's registry/context also includes the conditional historical routes.
P118 uses EXT09 separately; P120/P122/P125–P127, P129–P132, P219–P222,
P242/P243 and Phases 42–44 have no EXT08 dependency and remain unchanged.
The supersession checker rejects a new VERIFIED_THEOREM dependency on EXT08.

Seven Phase 20/21 evidence snapshots are pinned to their baseline Git blobs.
They and their old hashes are not rewritten. Old verifier success means
reproduction of the historical finite/metadata contract, **not** current
acceptance of EXT08. The registry links an explicit audit/impact record;
research-health checks it against the current ledger and immutable history.
The claim index remains generated, never a second authority.

The ledger's claim-audit issue creation was attempted through the connected
GitHub tool, but GitHub returned HTTP 403 (integration lacks issue-write
permission). This tracked report is the local claim-audit docket. No external
issue, author notification, or specialist response is claimed. Git publication
does not imply the authors have reviewed or agreed with the objection.

## 6. Reproducibility and independent finite evidence — E61

See [run record](../../../EXT08_SCOPE_AUDIT_RESULTS.md), the experiment manifest,
and the generator/verifier/test files linked there. The supplied bundle is
a proposal based on Phase 43; Phase 44 is preserved. All eight supplied file
hashes were checked. The supplied generator and verifier were read in full,
their logic audited, and adapted with attribution. This is representational
independence (homogeneous integer recurrence versus Fraction dynamics,
positional series and bit lifting), not a claim of independent authorship.

Both implementations reconstruct every declared model prefix. The verifier
uses explicit exceptions, not removable asserts. Mandatory source and block
families are checked separately, together with the actual cycles 1, -1, -5.
The negative cycle control prevents confusing C's escape with literal
negative Collatz iteration. Source code and exact snapshots are retained;
finite repeat absence is never the proof of aperiodicity.

## What this result does not prove

- It does not refute EXT08's rational 2-adic critical-density statement.
- It does not prove or disprove rationality of the three 2-adic sources.
- It does not produce an actual positive or negative nonperiodic integer orbit.
- It does not invalidate internal permanent-safe reduction or normalized height.
- It does not close H112/H72/H89/H133 or exclude nontrivial positive cycles.
- It does not prove or disprove the Collatz conjecture.

Next useful work is a repaired or independent proof of EXT08 retaining the
completion distinction, or ordinary-source/carry work using internal results
without EXT08. Repeating finite depth or equating limits is not such a repair.
