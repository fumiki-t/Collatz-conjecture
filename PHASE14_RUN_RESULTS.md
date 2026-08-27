# Phase 14: coalescent rewrite and H72 — run results

Branch: `feat/phase14-coalescent-rewrite`

Base commit: `7e6f637cb0bed954a5f50f71a1aa6c45b127dc8f`

Phase 14 proves the exact coalescent rewrite criterion, reduces a least
permanent-safe counterexample source to rewrite-irreducible initial addresses,
proves three auxiliary companion/shadow lemmas, and exhaustively audits every
renewal address with total `Q<=13`.  It does not prove H72, P80's
anti-concentration premises, or the Collatz conjecture.

The detailed mathematical proof is
[`research/audits/coalescent-rewrite/REPORT.md`](research/audits/coalescent-rewrite/REPORT.md).

## Accepted results

- P81 `VERIFIED_THEOREM`: `F_d(2^k x+m)=F_a(x)` exactly iff the lengths,
  odd counts, and corrections satisfy the stated integer equations; cylinder
  legality and positivity are separated.
- P82 `VERIFIED_THEOREM`: the least positive discrepancy-escaping
  permanent-safe counterexample source has only irreducible initial renewal
  addresses. Reducibility is a right ideal and accepted rewrites terminate.
- P83 `VERIFIED_THEOREM`: initial-run thresholds
  `13/9`, `137/81`, `43/27`, with equality words `110`, `111010`, and
  `111100`, plus `R(w)>5/3-(2/3)^r`.
- P84 `VERIFIED_THEOREM`: every nontrivial block has
  `z-z'>1/(12U+1)` and the corresponding reciprocal series is finite.
- P85 `VERIFIED_THEOREM`: the proposed moving-shadow denominator and gcd
  bounds hold at every `a_n>=1` index, hence eventually under P76. The
  unqualified `a_n=0` case remains open.
- E23 `VERIFIED_FINITE`: complete `Q<=13` rewrite, normal-form, pressure, and
  adversarial audit.
- NG24 `REFUTED`: coalescent equivalence is not preserved by arbitrary left
  block concatenation.
- H72 remains `OPEN`; P80 remains `CONDITIONAL`.

## Principal finite results

```text
addresses:                    30,084
(Q,r3) classes:               24,197
collision classes:             5,829
collision pairs / edges:       5,949
reducible addresses:           5,887
irreducible finite forms:      24,197
nonunique finite normal forms:      0
mandatory adversarial cases:   2,144
```

The minimum collision is

```text
1 | 110 | 1  ~  111100
2*73-65=3^4
F_111100(2x+1)=F_11101(x)
canonical sources 7 and 15; common endpoint 20
```

The only collision within a fixed block-count layer through `Q=13` is the
specified three-block pair at `Q=13`.  Its supplied starts 886,143 and
1,772,287 both reach 2,694,703 with the literal requested parity words.

Finite irreducible pressure decreases in every audited block layer, but the
late layers are dominated by the total-`Q` cap.  No asymptotic pressure or
closed transfer operator is claimed.

## Reproduction

```bash
.venv/bin/python src/phase14_search.py \
  --artifact-dir artifacts --max-total-q 13 --threshold-q 14
.venv/bin/python verifier/verify_phase14.py \
  --artifact-dir artifacts --output artifacts/phase14_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase14_properties.py tests/test_phase14_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

The verifier contains none of `phase14_search`, `from src`, or `import src`.
Tamper tests alter theorem examples, finite collision counts, threshold
constants, and the adversarial digest and require rejection.

## What this result does not prove

- general rewrite confluence or a unique normal form at unbounded `Q`;
- an asymptotic irreducible pressure estimate;
- either P80 canonical-representative bound;
- H72 or exclusion of nontrivial cycles;
- the Collatz conjecture.

`proves_collatz=false`.
