# Phase 15 independent audit — surplus-dominating ancestors

## 1. Status and scope

This audit treats the supplied Phase 15 note as an untrusted research
proposal.  It independently reconstructs the symbolic arguments and the
finite search.  The accepted labels are:

| ID | Status | Result |
|---|---|---|
| P86 | `VERIFIED_THEOREM` | A smaller safe coalescent ancestor with at least the target's terminal coefficient surplus contradicts minimality of a least permanent-safe escaping source. |
| P87 | `VERIFIED_THEOREM` | A shorter arbitrary coalescent target can be cut at its strict discrepancy valley to obtain a safe suffix; descent and positivity are checked separately. |
| P88 | `VERIFIED_THEOREM` | At fixed odd count, the endpoint residue is injective on odd-gap words with every gap in `{1,2}`. |
| E24 | `VERIFIED_FINITE` | Every coefficient-safe target and competitor through `Q<=17`, plus every relevant shorter same-Q arbitrary target, was exactly enumerated twice. |
| NG25 | `REFUTED` | Same-Q safe-target rewrites are complete for surplus dominance. |
| NG26 | `REFUTED` | An arbitrary coalescent target must itself be coefficient-safe to yield a useful reduction. |
| H72 | `OPEN` | No eventual extinction or positive-source exclusion was proved. |

The shortcut map convention is

\[
T(x)=\begin{cases}x/2&2\mid x,\\(3x+1)/2&2\nmid x.\end{cases}
\]

For a binary word `w` of length `L(w)` and odd count `Q(w)`,

\[
F_w(x)=\frac{3^{Q(w)}x+B_w}{2^{L(w)}},\qquad
c(w)=\frac{3^{Q(w)}}{2^{L(w)}}.
\]

Write

\[
\delta(w)=Q(w)\log 3-L(w)\log 2=\log c(w).
\]

A nonempty word is coefficient-safe when every nonempty prefix `v` has
`c(v)>1`.  This is equivalent to the repository's non-strict convention
because no nonempty equality `3^q=2^L` is possible.

## 2. P86: surplus-dominance principle

Let `C` be a nonempty class of positive ordinary sources satisfying all three
conditions below:

1. every nonempty shortcut prefix is coefficient-safe;
2. its discrepancy tends to `+infinity`;
3. after two sources reach the same positive endpoint, membership has the
   shared-future property relevant to a counterexample orbit.

By well-ordering, `C` has a least source `S`.  Suppose a safe initial word `d`
from `S` reaches `Y`, while a smaller positive `V<S` reaches the same `Y`
through a safe word `b`, and

\[
c(b)\ge c(d).
\]

For any future prefix `u` after `Y`, safety of `du` gives

\[
c(bu)=c(b)c(u)\ge c(d)c(u)=c(du)>1.
\]

The prefixes internal to `b` are safe by hypothesis.  Also

\[
\delta(bu)-\delta(du)=\delta(b)-\delta(d)\ge0,
\]

so discrepancy escape of the original tail is preserved.  The two paths have
the identical deterministic future after `Y`, hence `V` belongs to `C`,
contradicting the minimality of `S`.

This theorem is internal.  To apply it to every hypothetical nonperiodic
positive Collatz counterexample, the repository still uses the external
Garcia--Tal/Heppner sparsity input EXT07 and its conditional consequence P74
to obtain a permanent-safe escaping tail minimum.  Nontrivial cycles are a
separate branch.

### Right-suffix closure

If `d` is dominated by `b`, append a common future word `u`.  Whenever `du`
is coefficient-safe, every cross-boundary prefix of `bu` is safe by the same
coefficient comparison, and the endpoint remains common.  Thus domination is
a right ideal inside the legal safe language.  The unqualified statement for
an arbitrary suffix is false as a formulation because an arbitrary suffix can
make `du` unsafe; P87 records the necessary qualification.

## 3. P87: strict-valley suffix

Let an arbitrary finite word `a` have prefix discrepancies
`delta_0,...,delta_L`, with `delta_0=0`.  Distinct prefix times have distinct
discrepancies: equality would imply a nontrivial equality between a power of
2 and a power of 3.  Therefore the global minimum occurs at a unique time
`t`.

Assume `a` is a shorter same-Q coalescent target for a safe target `d`.
Then `L(a)<L(d)`, so

\[
\delta(a)=\delta(d)+(L(d)-L(a))\log2>\delta(d)>0.
\]

If `a` is unsafe, its unique minimum is negative and occurs at a proper time
`0<t<L(a)`.  Write `a=pb` with `|p|=t`.  For every nonempty prefix `v` of
`b`, uniqueness of the minimum gives

\[
\delta(v)=\delta(pv)-\delta(p)>0.
\]

Thus `b` is strictly coefficient-safe, and

\[
\delta(b)=\delta(a)-\delta(p)>\delta(a)>\delta(d).
\]

This proves the symbolic surplus statement.  It does not automatically prove
that `V=T^t(x)` is positive and smaller than `S`; the generator and verifier
check `V<S`, the literal words, and the common endpoint for each finite
certificate.

The named Q=15 example is reconstructed exactly:

```text
d = 11101011111111101000001
(Q,L,B,S,Y) = (15,23,28365139,1874247,3205946)

a = 1010110111111101011100
(Q,L,B,x,Y) = (15,22,50054837,937121,3205946)

p = 1010
b = 110111111101011100
(Q,L,B,V,Y) = (13,18,2430911,527131,3205946)
```

Here `2B(a)-B(d)=5*3^15`, `S=2x+5`, and `c(b)>c(d)`.

## 4. P88: `{1,2}`-gap endpoint injectivity

For odd-to-odd exponents `e_j in {1,2}`, put

\[
E_j=e_1+\cdots+e_j,
\qquad B_j=3B_{j-1}+2^{E_{j-1}},
\qquad r_j=B_j2^{-E_j}\pmod {3^j}.
\]

Then

\[
r_j=(3r_{j-1}+1)2^{-e_j}\pmod {3^j}.
\]

Modulo 3, `r_j=2` determines `e_j=1`, while `r_j=1` determines
`e_j=2`.  Having recovered the last exponent, exact division gives

\[
r_{j-1}=\frac{2^{e_j}r_j-1}{3}\pmod {3^{j-1}}.
\]

Backward induction reconstructs the whole exponent word.  Hence two distinct
finite `{1,2}`-gap words with the same fixed `Q=j` cannot have the same
canonical endpoint residue modulo `3^j`.  Coefficient safety is not needed by
this proof.  The result does not turn a compatible infinite 2-adic source into
a positive ordinary integer.

## 5. E24 exact finite audit

The generator and independent verifier enumerate every strict-safe word with
`Q<=17` and every possible length.  A candidate ancestor `b` reaches a target
endpoint `Y` precisely when its positive endpoint residue agrees modulo
`3^Q(b)`; its corresponding source is reconstructed rather than trusted.
Dominance is decided by the integer inequality

\[
3^{Q(b)}2^{L(d)}\ge 3^{Q(d)}2^{L(b)}.
\]

The first three count columns reproduce the supplied scratch note.  The final
column additionally permits competitors above the target layer but still
under the explicit cutoff `Q(b)<=17`.

| Q(d) | safe words | same-Q dominated | Q(b)<=Q(d) dominated | Q(b)<=17 dominated |
|---:|---:|---:|---:|---:|
| 4 | 7 | 1 | 1 | 2 |
| 5 | 12 | 2 | 2 | 8 |
| 6 | 30 | 6 | 10 | 24 |
| 7 | 85 | 18 | 39 | 70 |
| 8 | 173 | 36 | 72 | 127 |
| 9 | 476 | 98 | 234 | 358 |
| 10 | 961 | 193 | 417 | 690 |
| 11 | 2,652 | 524 | 1,306 | 1,953 |
| 12 | 8,045 | 1,581 | 4,419 | 6,086 |
| 13 | 17,637 | 3,428 | 8,704 | 12,919 |
| 14 | 51,033 | 9,841 | 27,739 | 38,173 |
| 15 | 108,950 | 20,793 | 53,041 | 77,839 |
| 16 | 312,455 | 59,191 | 167,037 | 215,667 |
| 17 | 663,535 | 124,513 | 320,168 | 320,168 |

At Q=6, the least named cross-Q witness is

```text
d=111110100: (Q,L,B,S,Y)=(6,9,697,287,410)
b=1:         (Q,L,B,V,Y)=(1,1,1,273,410)
c(b)=3/2 > 729/512=c(d).
```

At Q=4 a higher layer already matters:

```text
d=110110:  (Q,L,B,S,Y)=(4,6,85,59,76)
b=1110110: (Q,L,B,V,Y)=(5,7,251,39,76).
```

The strict-valley enumeration independently reproduces zero extra reductions
through Q=14, then 12 at Q=15, 90 at Q=16, and 233 at Q=17 beyond same-Q safe
targets.  All arbitrary candidates are generated from combinations, and every
accepted suffix is checked by literal shortcut iteration.

The Q=17 `{1,2}`-gap layer contains exactly 32,596 safe words.  Their endpoint
residues are pairwise distinct and none is dominated by a competitor with
`Q(b)<=Q(d)`.  This is finite evidence for the hard core, not an asymptotic
survival theorem.

## 6. Literature and novelty boundary

- Tristan Stérin's *Binary expression of ancestors in the Collatz graph*
  (arXiv:1907.00775v4, accepted at RP 2020) constructs regular expressions
  for binary ancestors with a fixed budget of odd steps and emphasizes carry
  propagation.  P88's backward finite residue decoder and Phase 15's
  source/endpoint reconstruction overlap that predecessor-language setting;
  no novelty claim is made.  Stérin does not supply the surplus-dominance
  least-source theorem or an all-depth H72 exclusion.
- Rozier--Terracol's *Paradoxical behavior in Collatz sequences*,
  *Discrete Mathematics* 349 (2026), 115167, studies finite
  coefficient/paradoxical behavior.  It motivates the safe-prefix setting but
  does not prove the required eventual surplus-frontier extinction.  Its
  heuristic finiteness language is not used as a theorem.
- Garcia--Tal/Heppner remains the external sparsity input EXT07 used only at
  the P86-to-nonperiodic-orbit boundary through P74.

## 7. Strategic interpretation

P86 strictly strengthens P82: the competing word need not have the same odd
count or be a complete renewal address, only a safe path to the same endpoint
with enough terminal surplus.  P87 makes unsafe coalescent targets usable
after an exact valley cut.  These two facts improve the finite pruning
language and expose a carry-sensitive, cross-Q frontier.

The finite data do not establish a decreasing recursion for that frontier.
In particular, the Q=17 layer cannot see competitors with Q>17.  The next
proof-relevant target is an all-depth recursion or ordinary-height separation
theorem that tracks at least endpoint residue, source representative, and
terminal surplus, and that survives NG21--NG24 and the `{1,2}`-gap core.

## What this result does not prove

- that every coefficient-safe word has a surplus-dominating ancestor;
- that the cutoff survivors persist or disappear at unbounded Q;
- an asymptotic frontier contraction, predecessor anti-concentration, or P80;
- exclusion of a positive permanent-safe nonperiodic orbit or H72;
- exclusion of the nontrivial-cycle branch;
- the Collatz conjecture.

`proves_collatz=false`.
