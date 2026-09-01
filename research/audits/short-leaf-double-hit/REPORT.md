# Phase 31 v2 audit — short-leaf double-hit transport

## Scope and status

This audit treats `phase31_short_leaf_double_hit_v2.md` as an untrusted
proposal.  It accepts only the cycle-side T31-A--D mechanism.  The H89
Hamming-shell and `q0` ballot computations are deliberately deferred to a
separate experiment.

Accepted labels are P191--P194 and E44.  H172, H133, and H89 remain open.
`proves_collatz=false`.

## 1. Conventions

Let `a=(a_0,...,a_q)` be a valid reduced profile with `a_0=a_q=0`.
At level `k`, the components are the maximal half-open intervals of
`{j:a_j>=k}`.  Their containment relation is a finite rooted forest.  Fix one
maximum-height index `p`; the component containing `p` at each level is the
spine.  Write

```text
J = total number of level components,
A = sum_j a_j,
h = max_j a_j,
B_h = sum_(r=1)^(h-1) floor(r/delta),
Sigma = A-J-B_h.
```

P167 supplies `Sigma>=0` and charges all component excess outside the chosen
spine to `Sigma`.

## 2. P191 — short-leaf pruning

Fix an integer `R>=1`.  Repeatedly select a nonspine leaf component `[u,v)`
with `v-u<=R` and subtract one on that interval.

A leaf has no active cell at the next level, so its profile values are
identically its level.  Lowering it deletes exactly that forest node.  At its
left and right boundaries the profile jump only becomes less severe, hence
positive exponent legality is preserved.  Deletions in incomparable subtrees
commute; an ancestor becomes eligible only after its descendants have been
deleted.  Thus the residual pruning core is independent of the choice order.

Let `K_R` be the deleted-node count and `E_R` the residual-node count.  Then

```text
K_R+E_R=J.
```

Every residual nonspine node contains a residual nonspine leaf.  No such leaf
has length at most `R`, so every residual nonspine node has excess length at
least `R`.  Total nonspine excess is at most `Sigma`, while the spine has `h`
nodes.  Therefore

```text
E_R <= h + floor(Sigma/R).
```

Reversing the deletions reconstructs the original shortcut word by local
segment rotations.  A deleted component covers at most `R` odd gaps; since
the reduced mechanical exponents are in `{1,2}`, its shortcut span is at most
`2R`.  This proves P191 for every valid reduced profile and every fixed `R`.

## 3. P192 — finite double-hit inequality

Let `n<=L` and `N_R=n+4R`.  Reconstruct the residual word from the mechanical
word using its `E_R` residual component rotations.  Their total mechanical
span is at most `2A`.  A rotation of span `d` changes at most `d+N_R-1`
cyclic starts of an `N_R`-window, hence the residual exceptional set obeys

```text
U_R <= min(L, 2A+E_R(N_R-1)).
```

A deleted short component changes at most `n+2R-1` starts of an `n`-factor.
Outside `U_R`, a factor hit by at most one deleted operation is determined by
a mechanical `N_R`-context, no operation or one odd-label length in
`{1,...,R}`, and a relative operation position.  Mechanical factors contribute
at most `N_R+1` contexts, giving

```text
B_R(n)=(N_R+1)(1+R(n+2R)).
```

If all `L` cyclic `n`-factors are distinct, at most `B_R(n)` nonexceptional
starts can have zero or one hit.  Double-counting the remaining starts and
using the exceptional-set bound gives exactly

```text
2L <= K_R(n+2R-1)
      +4A
      +2E_R(n+4R-1)
      +2B_R(n).
```

No floating-point decision occurs in this argument or its finite audit.

## 4. P193 — asymptotic area repair

Consider the P187 cycle regime: `q->infinity`, `L/q->ell in (1,2]`, a fixed
inverse-polynomial multiplier gap, and state-separation width
`n=h+O(log q)`.  On any subsequence with bounded `A/q^(2/3)`, write

```text
x = lim J/q^(2/3),
y = lim h/q^(1/3),
z = lim Sigma/q^(2/3).
```

For each fixed `R`, divide P192 by `q`.  The `A`, `B_R(n)`, and fixed-`R`
offset terms are `o(q)`, while P191 gives
`E_R/q^(2/3)<=z/R+o(1)`.  Thus

```text
2ell <= (x+z/R)y.
```

The quantifier order is essential: first take the cycle limit for each fixed
`R`, then let `R->infinity`.  This yields `xy>=2ell`.  Combining it with P167,

```text
liminf A/q^(2/3) >= x+z+y^2/(2(ell-1)),
```

and minimizing gives `z=0`, `y^3=2ell(ell-1)`, and

```text
liminf A/q^(2/3)
  >= 3(2ell)^(2/3)/(2(ell-1)^(1/3)).
```

This supplies the missing all-`R` proof of the previously recorded P187
constant.  The noncritical and EXT17-dependent critical numerical
specializations in P188 are unchanged.

## 5. P194 — repaired equality rigidity

At equality in P193, every convergent subsequence has `z=0`; hence
`Sigma=o(q^(2/3))=o(J)`.  At most `Sigma` nonspine components are
nonsingletons, and the spine contributes only `h=o(J)` nodes.  Therefore all
but `o(J)` components are nonspine singleton transports.

Apply P192 with `R=1`.  Here `E_1<=h+Sigma=o(q^(2/3))`, the exceptional
contexts have size `o(L)`, and `B_1(n)=O(n^2)=o(L)`.  Equality in the leading
constraint makes total singleton incidence `2L+o(L)`.  Factor distinctness
forces at least two incidences at all but `o(L)` starts, so all but `o(L)`
starts have exactly two.

If `chi_t` marks the singleton anchors and
`c_t=sum_(r=0)^n chi_(t+r)`, then

```text
c_(t+1)-c_t = chi_(t+n+1)-chi_t,
# {t: chi_(t+n+1)!=chi_t} <= 2 # {t:c_t!=2} = o(L).
```

Thus the sharp equality regime really has an approximate low-denominator
anchor grid.  A compatible noncoprime resonant resultant is still open.

## 6. Relation to NG40

NG40 remains a valid refutation of the old inference from one normalized
double-hit inequality.  Its exact countermodel has enough residual density to
saturate that old chain, but it fails the P191/P192 inequality family as
`R->infinity`: it does not satisfy `xy>=2ell`.  P191--P194 therefore bypass,
rather than erase, NG40.

## 7. Independent finite audit

The generator and verifier independently reconstructed the complete
positive-`D` cyclic exponent corpus through `q<=9`, all minimum-profile
rotations, `R in {1,2,3}`, and every cyclic width.

```text
cyclic classes                 7,398
minimum rotations             10,485
pruning reconstructions       31,455
width/pruning cases          522,870
distinct-factor cases        332,697
removed components            20,739
residual components           91,251
```

The verifier uses a different pruning order and separately implements
composition enumeration, reduced profiles, component forests, rotations,
contexts, incidences, and factor sets.  It imports no generator module.
Tampered theory, corpus, and overclaim artifacts are rejected by tests.

Finite agreement is regression evidence only; it is not the proof of the
unbounded statements.

## 8. Deferred H89 proposal

The Hamming-shell bounds, the claimed `q0` support values `3,206,029,887` and
`3,673,866,064`, and the contextual entropy consequence were not audited.
They remain `OPEN` candidates and are absent from the accepted claim set.

## What this result does not prove

The result does not construct the required resultant, exclude cycles above or
at the area frontier, close H172/H133/H89, eliminate either nonperiodic P69
branch, or prove or disprove Collatz. `proves_collatz=false`.
