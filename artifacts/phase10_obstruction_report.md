# Phase 10 obstruction report

This report does not claim a proof or disproof of the Collatz conjecture.

## Verified reductions

- P63 reduces the q0 two-sided residue condition to the single gap residue rho, with m=N and X=m+rho in the near box.
- P64 conditionally proves renewal safety through K0-1 for every least-counterexample orbit point in [N,N+W].
- P65 proves the exact formal rational-cycle minimum and gcd identity.

## Exact finite spacing obstruction

- The complete scan through H=1500000 has deepest defined spacing Delta_213=268416 at (1126015,1394431).
- At the next depth the scanned prefix has fewer than two safe starts. This is absence in a finite prefix, not a lower bound for larger H.
- The deletion/neighbor-gap recursion is exact, but no composable cylinder certificate proving the Phase 10 target was found.
- Strict per-depth spacing growth is false: Delta_2=Delta_3=4 in the production prefix. Only nondecrease survives.

## Open target

- C05 remains OPEN: Delta_(K0-1)(2^72)>4142380786 was not proved or computationally evaluated.
- The gap reduction does not determine B modulo D for the unknown q0 word, so C04 remains OPEN.

## What this result does not prove

Phase 10 does not prove C04, C05, the existence of a least counterexample, or the Collatz conjecture.
