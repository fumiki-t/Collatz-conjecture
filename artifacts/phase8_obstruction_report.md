# Phase 8 obstruction report

This report does not claim a proof of the Collatz conjecture.

## VERIFIED_THEOREM

- C02 is closed for every r,s>=1 by exact algebra, six CRT base cases, and EXT05 in the remaining Diophantine regime.
- The four consecutive-contact short-excursion maps are reconstructed exactly.

## CONDITIONAL / VERIFIED_FINITE consequences

- At most `5` defect/octave exceptions occur under P58, X02, and EXT04.
- At least `31327720457` odd iterates, `889748819` h=12 pairs, and `7308576455` short consecutive returns lie in the first octave.

## EXTERNAL_THEOREM / EXTERNAL_EVIDENCE

- EXT05 is Rozier--Terracol v5, Lemma B.1; its q>18 derivation uses Ellison. Phase 8 does not use the paper's finite q=13..18 check.
- EXT04 (Denjoy--Koksma) and X02 (N>V) remain external and are not reproved.

## OPEN

- C03 has no counterexample among `79184` contracting A/B words through block length `18`; `79166` of them contain both A and B.
- The all-word minimum descent margin is `1` at pure word `B`; the mixed-word minimum is `1249` at `BBA`.
- The separate block-boundary first-crossing search retains `12265` words through length `22`.

## Main obstruction

C02 closes the ordered A^rB^s family, but no common well-founded potential or transition theorem was found for arbitrary interleavings in {A,B}*. The octave bridge forces many short returns inside [N,2N), yet the four-map alphabet alone has no proved global frequency or rank constraint.

## What this result does not prove

It does not prove C03, H54, H57, exclude all hypothetical least-counterexample paths, or prove the Collatz conjecture.
