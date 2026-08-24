# Phase 9 obstruction report

This report does not claim a proof or disproof of the Collatz conjecture.

## Verified conditional structure

- P59: contact at an L-phase forces the next H-phase contact.
- The denominator-256 rational dual search gives the conditional contact lower bound `35251435772`.
- E14 gives `16848437652` first-octave short returns under its explicit dependencies.
- P60 gives `0<=d<=4142380786<2^32` only in the q0 first-crossing case.
- P61 forces endpoint residues 7 or 19 modulo 36 and forbids G4 in a least-counterexample first-octave return.
- P62's first coefficient pair not excluded by the uniform reverse threshold is `(a,L)=(615582794569,975675645481)`.

## Refuted contact-only shortcut

- NG17: forced closure plus weighted pressure is consistent with a symbolic all-contact critical word. Endpoint and least-residue arithmetic are indispensable.

## Open two-sided obstruction

- C04 remains OPEN after exact first-crossing enumeration through q=21 (22475497 words).
- Storage deviation: individual rows are not all materialized; ordered per-layer digests plus extrema/candidates are stored, and the independent verifier re-enumerates every row.
- The direct paradoxical tree through shortcut length 21 found no new rank and no C04 counterexample.
- Full arbitrary reverse-exponent residue enumeration through a=30 was not achieved; all coefficient pairs were audited, while residue rows are explicitly limited to the lower-mechanical family.

## Main bottleneck

No theorem links the near-diagonal 2-adic/3-adic box to an impossibility at q0. Contact density and reverse coefficient barriers are strong but do not control simultaneous ordinary residue size.

## What this result does not prove

Phase 9 does not establish C04, construct the q0 word, prove paradoxical-tree finiteness, or prove/disprove Collatz.
