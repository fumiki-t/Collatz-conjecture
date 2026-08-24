# Phase 12 obstruction report

This report does not claim a proof or disproof of the Collatz conjecture.

## Finite orbit audit

- Starts: 25000 values S=3 mod 4 through 100000.
- Longest recorded coefficient-safe tail-minimum prefix: 85 odd iterates at S=35655.
- Finite coefficient first crossings: 25000.
- Mandatory adversarial instances: 2144.

## Exponent obstruction

The residue-packing input is sharp at exponent 1/9.  The abstract sequence of
all positive integers coprime to six has two members in each complete block of
six, so its reciprocal sum has leading coefficient 1/3.  Combined with the
factor 1/3 in log(1+1/(3x)), this gives Y_j of order j^(1/9).  Therefore a
stronger exponent cannot follow from distinctness and gcd(x_i,6)=1 alone.

This abstract saturator is not a Collatz orbit.  H72 remains open: exploit
transition congruences or multi-step exclusions that actual odd orbits obey.

## All-contact word

The critical upper mechanical word is impossible as an infinite positive
integer trajectory by P72, even though every finite prefix has a canonical
2-adic residue.  This removes one extremal word, not the full safe language.

## What this result does not prove

Phase 12 does not exclude arbitrary infinite coefficient-safe tails,
nontrivial cycles, the renewal ladder, or the Collatz conjecture.
