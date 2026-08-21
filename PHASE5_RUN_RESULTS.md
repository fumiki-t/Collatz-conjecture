# Phase 5 acceptance run

Branch: `feat/phase5-dangerous-cycles`

Phase 5 combines independently verified finite-state algebra with a
non-exhaustive depth-40 shadow search. It does not prove the Collatz conjecture.

## Reproduction commands

```bash
.venv/bin/python src/phase5_search.py \
  --direct-bound 16777216 --shadow-depth 40 \
  --beam-width 256 --low-precision-limit 4 \
  --mixed-block-u-bound 20000
.venv/bin/python verifier/verify_phase5.py \
  --artifact-dir artifacts \
  --output artifacts/section4_verifier_result.json
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts --write artifacts/SHA256SUMS
```

## Tests

```text
145 passed in 71.79s (0:01:11)
```

The tests include exact affine-family properties, all 52 first-return
templates, all 108 simple cycles, the return-20 envelope, every section integer
below `2^24`, independent-verifier acceptance, and tamper rejection.

## Independently verified results

- Deleting `{1,11,20,26}` from the colored unit graph modulo 27 leaves an
  acyclic graph. First returns have length at most 9.
- The independently regenerated first-return dictionary contains exactly 52
  labeled templates.
- The full unit graph has 108 labeled simple cycles modulo cyclic rotation.
  Exactly `1`, `101`, `1101`, and `011101` have multiplier at least one.
- Every other simple cycle has multiplier at most `27/32`.
- Among positive 20-to-20 paths with no internal 20 or 26, `101` is the unique
  noncontracting simple path. Every other path satisfies
  `R(x) <= (27x+46)/32 < x`.
- The direct audit checked all 2,485,513 section integers below `2^24`, totaling
  7,162,840 shortcut steps. Its digest is
  `588b40e626d5dbf165dcb1e0f8e157742b2d43a5e4ddc26b4f4384187c51c2ef`.
- The independent verifier reconstructed 832 shadow identities, 9,941 retained
  exact paths, 160 dangerous-cycle repetition families, and all eight
  mixed-block multiplier records. Its best finite mixed-block bound is
  `multiplier - 1 < 2^-13`.

The verifier result is `valid: true`, with status
`verified_phase5_algebraic_certificates_with_bounded_heuristics_unresolved`.

## Bounded observations and obstacles

- The deterministic shadow search used beam width 256 through return depth 40;
  it is not exhaustive.
- The quantified H5-A surrogate failed on 2,141 retained paths. The smallest
  recorded counterexample is the depth-20 family
  `461826978031 + 474989023199232*t`; its maximum aligned dangerous-cycle run
  is only 2.
- The bounded H5-B test found 80 candidates. The smallest is a depth-5 path
  starting at 362,638, switching `C146 -> C23` with valuations `9 -> 11`.
- These results do not refute the original H5-A/H5-B text because “long”,
  “fixed contraction”, and “arbitrarily high” were not quantitatively defined.
- The smallest nontrivial low-precision switch witness is `11 -> 26`, switching
  `C7 -> C146` with valuations `1 -> 2`.
- CEGAR did not synthesize a universal well-founded ranking in the tested
  languages. Exact adversarial families for arbitrary repetitions of all four
  dangerous words are retained; failure of these candidate languages is not a
  theorem that no other ranking exists.
- Required mixed-block family `A=11101`, `B=1100` was audited separately.
  `W=AB=111011100` has map `(729x+817)/512` and fixed point `-817/217`, which
  is not one of the four canonical shadow centers.
- Exact integer search through `u<=20000` produced eight successively closer
  multipliers above one. The last record is `(r,s)=(184,297)`, has return depth
  1,146, has no aligned canonical dangerous-cycle run longer than one, and has
  multiplier excess below `2^-13`.
- The arbitrary-closeness conclusion is separated from the finite records: it
  uses the exact irrationality reduction for
  `log(81/32)/log(16/9)` plus the named irrational-rotation density theorem.
  This refutes four-center completeness and the quantified H5-A surrogate; for
  H5-B it is an obstruction to the four-center ranking interpretation, not by
  itself a proof or disproof of the original unquantified statement.

## Phase 5 SHA-256

```text
34855b28bbed9f6348100c7abb1d549582949da6b7c072f435b71a4e2db773e2  phase5_obstruction_report.md
5eb408b6509ef010bb6029b0e6af0c5d7b85d57c44be9198e6847450a1cd80b5  return20_domination.json
aa04e4171232873127793dbd9d6ec1294ebdadeee0d131822f13c74069c96fa8  section4_templates.json
84af08ba355f970e0a74e8a046bad27faddaba9dab4cbbcd252a9e9d8f7e8cea  section4_verifier_result.json
9ccc8774f0cf86a6162edd0cec2e8378c4eacc60025ca385da575c50f495563f  shadow_switch_counterexamples.json
74890ae9c2876ee5c524321d7967e57c9948d98811da41b111b4d15b88141d61  shadow_transfer_matrix.json
d2e3904fe29e73bedf1f4b086ebb78832e919a3b0bb55680330e8fb3752d899b  simple_cycles_mod27.json
```

The complete manifest is `artifacts/SHA256SUMS`; its own SHA-256 is
`3b4b63767a2663a19121a00444a052fd235e289d04cd7bee236f84550b8ff6b1`.
