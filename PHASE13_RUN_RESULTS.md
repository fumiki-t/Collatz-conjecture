# Phase 13: renewal code, weighted pressure, and canonical residues

Phase 13 independently reconstructed two untrusted scratch audits and accepted
only the statements supported by a separate proof and independent verifier.

## Result

- P77 `VERIFIED_THEOREM`: unique strict-suffix renewal decomposition and
  reversed first-upcrossing prefix code.
- P78 `VERIFIED_THEOREM`: weighted stopping identity and
  `kappa<3/4`, `sigma<7/12`, `tau<19/96`, `nu<9/32`.
- P79 `VERIFIED_THEOREM`: `R(w)>=13/9`, equality only for `w=110`, the
  positive-source bridge, and exact normalized correction/valuation rules.
- P80 `CONDITIONAL`: either explicitly quantified canonical-residue
  anti-concentration premise would exclude the permanent-safe positive branch.
- E22 `VERIFIED_FINITE`: exact DP and bounded residue/countermodel audit.
- NG23 `REFUTED`: coefficient-one raw Haar volume controls canonical positive
  representatives; the least obstruction is `u=1`, `H=2`, prediction `2/3`.
- NG22 remains `REFUTED`; the square-root countermodel is additional evidence.
- H72 remains `OPEN`.

The detailed proof audit is
[`research/audits/renewal-code-pressure/REPORT.md`](research/audits/renewal-code-pressure/REPORT.md).

## Exact finite scope

- first-passage DP through length 512;
- every first-upcrossing word and address with total `Q<=12` and 1–4 blocks;
- ordinary heights `1<=H<=2048`;
- 4096 odd steps of the square-root critical countermodel;
- 2144 mandatory adversarial convention instances.

The independent verifier reports:

```json
{
  "valid": true,
  "P77": "VERIFIED_THEOREM",
  "P78": "VERIFIED_THEOREM",
  "P79": "VERIFIED_THEOREM",
  "P80": "CONDITIONAL",
  "E22": "VERIFIED_FINITE",
  "NG23": "REFUTED",
  "NG22": "REFUTED",
  "H72": "OPEN",
  "proves_collatz": false
}
```

## Reproduction

```bash
.venv/bin/python src/phase13_search.py \
  --artifact-dir artifacts --dp-length 512 --max-total-q 12 \
  --max-blocks 4 --height 2048 --critical-steps 4096
.venv/bin/python verifier/verify_phase13.py \
  --artifact-dir artifacts --output artifacts/phase13_verifier.json
.venv/bin/python -m pytest -q tests/test_phase13_properties.py \
  tests/test_phase13_verifier.py tests/test_research_health.py
```

## What this result does not prove

- the anti-concentration estimates assumed by P80;
- nonexistence of a positive ordinary permanent-safe source;
- H72;
- exclusion of nontrivial cycles;
- the Collatz conjecture.

`proves_collatz=false`.
