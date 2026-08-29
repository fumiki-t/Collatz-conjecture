# Phase 19 obstruction report

## NG31 — average-small affine correction (`REFUTED`)

Under the endpoint tilt `P_+(e)=3/4^e`, the coefficient first-passage
correction has infinite first moment for every threshold `t>1`.  The proof is
not a tail fit: bounded stopping gives

```text
E_+ beta_(T_t cap R) = (1/3) E_- (T_t cap R),
```

while the source-tilt nonnegative coefficient martingale has
`P_-(T_t=infinity)>=1-1/t`.  Monotone convergence forces the mean to diverge.
Fractional moments below one remain finite.  Thus averaged affine correction
cannot be inserted as a uniformly small error into a Haar-volume argument.

## H112 — infinite geodesic nonzero lifts (`OPEN`)

P115 characterizes positive ordinary realizability by eventual zero source
lifts, but does not prove that every infinite all-prefix same-Q-geodesic safe
branch has infinitely many nonzero lifts.  The exact source-167 Q=17 word has
eleven trailing zero exponent lifts and then crosses coefficient safety three
shortcut steps later.  It prevents any finite zero-run rule from being
promoted to eventual stabilization.

## Remaining affine-only band

P112 finds a smaller safe valley ancestor unless

```text
n > 3N(1-c/u).
```

This localizes short predecessors to a near-diagonal coefficient band but does
not empty the band.  H104/H105/H89 still need ordinary source, endpoint,
carry, and height information.

## Periodic scope repair

P116 applies to a repeating block containing an odd step.  The all-zero block
has fixed point zero; it is not a positive odd cycle candidate.  For a reduced
rational 2-adic fixed source that is not a positive integer, the elementary
congruence already gives exponential canonical-residue growth.

## What this result does not prove

It does not prove H112, H72, H89, H104, H105, exclude the nontrivial-cycle
branch, or prove the Collatz conjecture. `proves_collatz=false`.
