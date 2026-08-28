# Phase 15B audit: ancestral-minimal frontier

**Status:** accepted mathematical derivations plus bounded exact computation

**Map:** full shortcut map `T(n)=n/2` for even `n` and `(3n+1)/2` for odd `n`

**Arithmetic:** integers and exact rationals for every acceptance decision

**Collatz status:** `OPEN`; `proves_collatz=false`

The supplied `phase15b_ancestral_frontier_note.md` was treated as an
untrusted research proposal, not as evidence. Its reusable claim IDs P86--P88
were rejected because those IDs already belong to Phase 15. This audit assigns
P89--P96, H89, E25--E26, and NG27 and rederives every accepted statement.

## 1. Conventions

For a binary parity word `w=s_0...s_(L-1)`, let `Q(w)` be its number of ones
and define

\[
F_w(x)=\frac{3^{Q(w)}x+B(w)}{2^{L(w)}}.
\]

Concatenation is chronological: `ab` means first `a`, then `b`, and

\[
B(ab)=3^{Q(b)}B(a)+2^{L(a)}B(b).
\]

A nonempty word is **coefficient-safe** when
`3^{Q(prefix)}>2^{L(prefix)}` for every nonempty prefix. Its least positive
literal source and endpoint representatives are reconstructed from

\[
r_2\equiv-B3^{-Q}\pmod {2^L},\qquad
r_3\equiv B2^{-L}\pmod {3^Q}.
\]

For positive `n`, define `mu(Y)` as the least positive source of a nonempty
safe path ending at `Y`, when one exists. Define the extended-integer depth

\[
A(n)=\sup\{k\ge0:\mu(T^j(n))=n\text{ for }1\le j\le k,
\text{ and the first }k\text{ prefixes are safe}\}.
\]

The supremum may be infinity. Finally,
`M_star(k)=min{n>=2:A(n)>=k}`. This infinity convention repairs the note's
plain `max`, which is undefined for a permanent-safe source.

## 2. P89 — ancestral minimality

**Classification:** `VERIFIED_THEOREM`.

Let `N` be a least positive Collatz counterexample and let a coefficient-safe
prefix from `N` end at `Y`. If a positive `x<N` has a coefficient-safe path to
the same `Y`, then the deterministic future of `x` after reaching `Y` is the
future of `N`. That future never reaches 1. A trajectory that had reached 1
earlier could only remain in the shortcut cycle `1,2`, and hence could not
later reach the safe endpoint `Y>N>=3`. Thus `x` is a smaller positive
counterexample, a contradiction. Therefore `mu(Y)=N` along every safe prefix
of `N`.

The safe qualification is needed by the definition of `mu`, not by the
shared-future contradiction itself. No nonperiodicity assumption is used.

## 3. P90/H89 — strengthened barrier and repaired two-case route

**P90 classification:** `CONDITIONAL`.

**H89 classification:** `OPEN`.

Because ancestral safety is stronger than coefficient safety,
`M_star(k)>=M(k)`. Under P54's least-counterexample finite-first-crossing
hypotheses,

\[
M_\star(K_q-1)\le N\le H_q.
\]

The supplied note did not explicitly close the never-crossing case. The
repair uses two already audited facts. P89 gives `A(N)=infinity` for a
least counterexample whose coefficient is permanently safe, hence
`M_star(K_q-1)<=N` for every `q`. Phase 6 proves `H_q>q/6`; choosing large
`q>6N` would contradict any eventual inequality

\[
H89:\qquad M_\star(K_q-1)>H_q.
\]

Thus an eventual H89 theorem, together with an independently checked finite
remainder for finite crossings, would exclude both coefficient-crossing
possibilities for a least counterexample. H89 itself is not proved here.

## 4. P91 — cross-Q identity and prefix carry

**Classification:** `VERIFIED_THEOREM`.

Suppose `Q(d)=Q(a)+s` and `L(d)=L(a)+k`. Directly clearing denominators gives

\[
F_d(y)=F_a(x)
\iff
3^s y=2^k x+m,
\quad
2^kB(a)-B(d)=3^{Q(a)}m.
\]

For a common chronological prefix `p`, the same relation lifts precisely when

\[
3^{Q(p)}\mid (2^k-3^s)B(p)+2^{L(p)}m.
\]

The quotient is the new carry `M`. This follows by substituting the exact
concatenation formula for `B(pa)` and `B(pd)`. Divisibility is only the carry
condition; positivity, literal-cylinder membership, source descent, and
coefficient safety remain separate obligations.

The audited witness is

```text
d=111110100: (Q,L,B,source,endpoint)=(6,9,697,287,410)
a=1 at endpoint 410: source 273
3^5*287 = 2^8*273 - 147
2^8*1 - 697 = 3*(-147).
```

## 5. P92 — uniform cylinder dominance

**Classification:** `VERIFIED_THEOREM`.

For an endpoint `Y` in a word's endpoint cylinder, its source is

\[
g_w(Y)=\frac{2^{L(w)}Y-B(w)}{3^{Q(w)}}.
\]

If the endpoint cylinder of `d` is contained in that of `a` and
`c(a)=3^{Q(a)}/2^{L(a)} >= c(d)`, then

\[
g_d(Y)-g_a(Y)
\]

is affine in `Y` with nonnegative slope `1/c(d)-1/c(a)`. If the `a` source is
already smaller at the first positive `d` endpoint, it remains smaller at
every later occurrence in the `d` cylinder. The theorem does not manufacture
cylinder inclusion, positivity, or safety.

## 6. P93/P94 — finite renewal decomposition and Beatty support

**Classification:** both `VERIFIED_THEOREM`.

Write the exact discrepancy of a prefix as

\[
\Delta_j=Q_j\log 3-j\log 2.
\]

For a finite safe word, choose the unique minimum of `Delta_j` over the
remaining nonempty suffix of prefix times, cut there, and repeat. Distinct
prefix discrepancies cannot tie because `3^u=2^v` has no nonzero solution.
Each resulting block is safe. Every proper suffix of a block has coefficient
below one relative to the whole block, so reversing it gives a word whose
proper prefixes satisfy `3^q<=2^L` and whose whole word satisfies `3^q>2^L`.
The successive unique minima also prove uniqueness of the decomposition.

For a nontrivial reverse first-upcrossing word with `q` ones and length `L`,
the final bit is one. The last proper-prefix and whole-word inequalities give

\[
\lfloor(q-1)\alpha\rfloor+2\le L\le\lfloor q\alpha\rfloor,
\qquad \alpha=\log_2 3.
\]

The interval is nonempty only when
`floor(q beta)=floor((q-1) beta)+1`, where `beta=log2(3/2)`, and then it has
the single value `L=floor(q alpha)`. Certificate decisions compare integer
powers of 2 and 3; logarithms only describe the proved inequalities.

## 7. P95 — shifted correction and jump coalescence

**Classification:** `VERIFIED_THEOREM`.

Set

\[
D(w)=B(w)+2^{L(w)}-3^{Q(w)}.
\]

Then

\[
F_w(z)+1=\frac{3^Q(z+1)+D(w)}{2^L},
\]

and exact composition gives

\[
D(ab)=3^{Q(b)}D(a)+2^{L(a)}D(b).
\]

If `w` starts with `r` ones followed by zero, write `w=1^r0v`.
Since `D(1^r)=0` and `D(0)=1`, the composition formula gives
`D(w)=2^r` times an odd integer; hence `v2(D(w))=r`.

For equal-Q words with `L(d)=L(a)+k`, substituting
`y+1=2^k(x+1)` into P81 gives

\[
F_d(y)=F_a(x)\iff D(d)=2^kD(a).
\]

Thus `(Q,L-r,D/2^r)` is the exact jump class. The identity is preserved by a
common right suffix and by a common left all-one prefix. General left prefixes
still require P91's carry test; NG24 is not bypassed.

## 8. P96 — 3-adic endpoint measure

**Classification:** `VERIFIED_THEOREM`, using the already proved P78 pressure
bound.

Every finite safe word has P93's renewal decomposition. Its final endpoint is
therefore in the endpoint cylinder of its last renewal block. Conversely, a
positive ordinary occurrence of a renewal-block cylinder has a positive
literal safe predecessor. The 3-adic union is consequently covered by the
renewal-block endpoint cylinders. P78 gives

\[
\mu_3(\text{covered endpoints})
\le\sum_{u\in U}3^{-Q(u)}=\sigma<\frac7{12}.
\]

Every such endpoint is a 3-adic unit. Since the unit space has measure `2/3`,
its uncovered measure is greater than `1/12`, or greater than `1/8`
conditionally inside the units.

This is a Haar-measure statement, not a pointwise theorem. All positive
ordinary integers form a countable measure-zero set and could still lie in a
smaller-measure 3-adic union.

## 9. E25 — exact source scan

**Classification:** `VERIFIED_FINITE`.

Every odd source `n<=5,000,000` was followed through its complete
coefficient-safe prefix. There was no endpoint-height cutoff. For each tested
endpoint the generator records the least source; the independent verifier
reconstructs the same map by scanning sources in descending order.

```text
odd sources:                 2,500,000
safe source-endpoint pairs: 12,443,880
distinct endpoints:         5,297,663
largest endpoint:           659,401,147,466
maximum ancestral depth:    209
M_star(210):                > 5,000,000
termination by crossing:    1,114,526
termination by domination:  1,385,473
```

The coefficient-depth record at source 1,126,015 is 223 but its ancestral
depth is only 66: a smaller source 1,042,431 reaches the common endpoint
67,625,867 safely. At source 1,394,431, ancestral depth 209 ends at endpoint
7,283,621, reached from source 1,278,879 in seven safe steps. These examples
show why `M_star` is strictly stronger than the old coefficient-only `M`.

The finite inequality does not imply eventual growth of `M_star`.

## 10. E26/NG27 — finite frontier, trie, and compression

**E26 classification:** `VERIFIED_FINITE`.

**NG27 classification:** `REFUTED`.

All 663,535 safe words at Q=17 were reconstructed. Of them, 124,513 have a
same-Q uniform dominator, and 320,168 have a uniform dominator with ancestor
Q no larger than target Q. The shifted-jump rule detects 124,509.

The primitive renewal endpoint-cylinder counts through Q=17 are

```text
Q:      1  2 3 4 5 6 7 8  9 10  11  12 13   14 15    16 17
new:    1  1 0 1 0 2 8 0 28  0 124 602  0 2498  0 12319  0
```

Their exact finite union mass is `20113810/43046721`; conditional unit
coverage is `10056905/14348907` (approximately 0.7008830011). These numbers
are sanity data, not inputs to P96.

The proposed universal finite pattern “same-Q total compression gain is at
most three” first fails in the audited Q=19 layer. Among maximum-gain rows the
artifact chooses least target source, making NG27's representative canonical.
The exact witness has gain four and satisfies

```text
y+1 = 16*(x+1).
```

This local gain need not compose and gives no asymptotic contraction.

## 11. Independent verification and falsification boundary

The generator uses packed integer words and an ascending source scan. The
verifier imports none of the generator and uses literal string words plus a
descending source scan. It reconstructs every artifact, the exact digests,
all canonical representatives, and the obstruction report. Tamper tests alter
theory, ancestral, frontier, renewal, compression, adversarial, and Markdown
evidence and require rejection.

The mandatory families `2^m-1`, `8^m-5`, `(110|111)^*`, `A=11101`,
`B=1100`, and `A^rB^s`, together with prior NG19 and NG21--NG26 boundaries,
are retained. Passing a finite regression is not a universality proof.

## What this result does not prove

- H89 or any eventual lower bound for `M_star`;
- that every safe word has a smaller uniform ancestor;
- a finite-state all-depth closure under arbitrary prefixes;
- P80, H72, or exclusion of a positive permanent-safe source;
- exclusion of nontrivial cycles;
- the Collatz conjecture.

`proves_collatz=false`.
