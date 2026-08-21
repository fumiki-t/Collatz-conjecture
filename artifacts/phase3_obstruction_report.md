# Phase 3 mixed-modulus obstruction report

This is an independently checkable finite computation, not a proof of the Collatz conjecture.

## Proved by the independent verifier

- Every recorded TERNARY_SPLIT is an exact, disjoint, exhaustive partition of its parent parameter domain.
- Every accepted REVERSE_MERGE has exact divisibility, positivity, strict-smaller-family inequalities, and an independently reconstructed forward affine path.
- OPEN records are unresolved and carry no proof claim.

## Exhaustive finite observations

- Coefficient DP checks all pass: `True`.
- Binary depth 20 generalized Ballot nodes: `27328`.
- Stage A binary REVERSE_MERGE closures: `11458`.
- Preliminary all-parent ternary audit: `50244/81984` children merge.
- Actual Stage B children: `47610`; closed `15870`; refined `31740`.
- Actual Stage C children: `95220`; closed `15870`; OPEN `79350`.
- Existing Phase 1 domain-zero boundary margins are positive: `True`.
- Boundary-gap exact audit reaches boundary depth `36`; counterexample: `None`.
- Smallest finite-range boundary gap: `1` at boundary depth `5`.
- `(110|111)^*` words checked: `4096`; coefficient violations: `0`.

The Phase 2 OPEN frontier through depth 26 is exactly the coefficient-nonshrinking generalized Ballot language, not an arithmetically exceptional subcollection. The earlier 88% periodic-shadow statistic is therefore not a certified macro coverage rate.

## Exact remaining obstruction

- Smallest unresolved represented integer: `27`.
- Family: `n(t)=27+9437184*t`, `t >= 0`.
- Endpoint: `T^20(n(t))=395+129140163*t`.
- Binary parity word: `11011111010110111011`; ternary path: `[0, 0]`.
- This is an exact obstruction only to the bounded Phase 3 rule search, not an infinite Collatz obstruction theorem.

## Growth and closure interpretation

- Level 0 unresolved parents after closure: `15870`.
- Level 1 unresolved children after merge attempts: `31740` (`31740/15870`).
- Level 2 OPEN children: `79350` (`79350/31740`).
- The tested mixed-modulus unresolved population is supercritical/exponential-looking, not subcritical; no asymptotic classification is proved.
- All accepted closures use REVERSE_MERGE without a periodic-substring dictionary: `43198/43198` (100% of closures). Stage A alone closes `11458/27328` original binary parents; later levels count ternary descendants.

## Heuristic and conjectural status

- No beam-search value is included in proof data. The depth-54 beam observation from the brief is not reproduced here.
- The boundary-gap positivity hypothesis has only the finite exhaustive scope recorded in JSON.
- A meaningful next rule must address the exact mixed survivors, likely by a ranked recursive dependency or a more general reverse-preimage lattice relation; increasing only the split depth is not enough.
