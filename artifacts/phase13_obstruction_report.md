# Phase 13 obstruction report

Phase 13 does not prove or disprove the Collatz conjecture.

## Exact failed mechanism

The raw coefficient-one Haar-volume estimate fails for the first codeword
`u=1`.  Its source representative is 1 modulo 2, its endpoint representative
is 2 modulo 3, and at ordinary height `H=2` the canonical count is 1 while
both raw volume predictions equal `2/3`.

This is a local obstruction to coefficient one and a fundamental obstruction
to identifying local Haar mass with control of one designated positive
integer.  It does not refute an estimate with an unspecified fixed constant.

## Surviving conditional route

An endpoint count bounded by `exp(epsilon*i) H sigma^i`, or a two-sided count
bounded by `exp(epsilon*i) H^2 tau^i`, would combine with renewal growth to
exclude a permanent-safe positive orbit.  Phase 13 proves only this
implication.  The anti-concentration premise remains open.

## Additional exact structure

For a nontrivial renewal block, the normalized correction
`C_w=(B_w+2^L-3^q)/4` is integral, satisfies `C_w>=2^(L-3)`, and has
`v2(C_w)=r-2`, where `r` is the initial run of ones.  This produces a genuine
ordinary-integrality transition rule but no closed anti-concentration bound.

## What this result does not prove

- the endpoint or two-sided anti-concentration theorem;
- nonexistence of a positive ordinary permanent-safe source;
- H72;
- exclusion of nontrivial cycles;
- the Collatz conjecture.

`proves_collatz=false`.
