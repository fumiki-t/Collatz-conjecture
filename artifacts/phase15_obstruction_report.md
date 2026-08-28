# Phase 15 obstruction report

Phase 15 does not prove or disprove the Collatz conjecture.

## Cross-Q obstruction to same-layer completeness

The safe target `111110100` has `(Q,L,B,S,Y)=(6,9,697,287,410)`.
The one-bit safe ancestor `1` reaches the same endpoint from 273 and has
coefficient `3/2 > 3^6/2^9`.  Therefore same-Q coalescent rewrites are not a
complete surplus-dominance test.  A second example has a Q=5 ancestor
dominating a Q=4 target.

## Unsafe-target obstruction

The Q=15 arbitrary target `1010110111111101011100` is not coefficient-safe.
Cutting after its strict discrepancy valley `1010` yields the safe suffix
`110111111101011100`, which coalesces below the named safe target and has
larger terminal surplus.  Thus a search may not discard arbitrary targets
before the valley extraction.

## Cutoff obstruction

The finite frontier is complete only for competitor odd count `Q_b<=17`.
Survivors in the top layers can still be dominated by an unenumerated
higher-Q ancestor.  Finite survivor counts are not an asymptotic theorem.

## What this result does not prove

- eventual extinction of the surplus-undominated frontier;
- either anti-concentration premise in P80;
- exclusion of a positive permanent-safe source or H72;
- exclusion of nontrivial cycles;
- the Collatz conjecture.

`proves_collatz=false`.
