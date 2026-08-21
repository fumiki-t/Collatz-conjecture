# Phase 5 dangerous-cycle obstruction report

This report does not claim a proof of the Collatz conjecture.

## Proved by the independent verifier

- Deleting residues `{1,11,20,26}` from the colored unit graph modulo 27 leaves a DAG.
- Its exact first-return system has 52 templates and maximum return length 9.
- The full unit graph has 108 labeled simple cycles up to rotation. Exactly `1`, `101`, `1101`, and `011101` are noncontracting.
- Every other simple cycle has multiplier at most `27/32`.
- The return-20 domination statement is verified: `101` is the unique noncontracting simple return, and every other path is bounded by `(27x+46)/32<x`.
- All 52 affine maps, fixed points, cylinder domains, shadow-transfer identities, and stored exact paths are reconstructed from parity words.

## Exhaustive finite computation

- Direct template comparison below `2^24`: 2485513 section integers and 7162840 shortcut steps.
- Direct audit digest: `588b40e626d5dbf165dcb1e0f8e157742b2d43a5e4ddc26b4f4384187c51c2ef`.
- Exact low-precision shadow refill transitions were exhaustively searched through source precision 4 under the recorded parameter moduli.

## Heuristic bounded search

- Shadow-switch search reached return depth 40 with deterministic beam width 256; it is not exhaustive.
- H5-A bounded surrogate survives: `False`; the original unquantified conjecture remains unresolved.
- Minimal H5-A surrogate counterexample: return depth `20`, source family `461826978031+474989023199232*t`, maximum aligned dangerous repetition `2`.
- H5-B bounded test survives: `False`; the original arbitrary-precision conjecture remains unresolved.
- Minimal H5-B bounded candidate: return depth `5`, start `362638`, `C146->C23` with valuations `9->11`.
- No bounded beam result is promoted to a universal certificate.

## Exact obstruction and failed ranking synthesis

- Smallest nontrivial low-precision switch witness: start `11`, end `26`, `C7->C146` with valuations `1->2`.
- Arbitrary repetition families are generated exactly for all four dangerous words; the artifact records repetitions through depth 40.
- Ranking synthesis result: `no_universal_well_founded_rank_synthesized`.
- This failure rejects only the tested rank languages. It is not a theorem that no ranking exists.

## Conjectures

- H5-A and H5-B require quantitative definitions before they can be certificate claims.
- A future proof rule would need a symbolic switch-cost lemma valid for arbitrary precision and repetition count.
