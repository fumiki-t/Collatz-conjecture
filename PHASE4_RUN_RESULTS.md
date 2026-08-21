# Phase 4 acceptance run

Branch: `feat/phase4-return9`

This is an exact finite first-return search on `n = 2 (mod 9)`. It retains an
explicit unresolved frontier and an infinite-code overflow beyond the
configured dictionary. It does not prove the Collatz conjecture.

## Reproduction commands

```bash
.venv/bin/python src/phase4_search.py \
  --max-a 8 --return-depth 3 \
  --direct-bound 16777216 --stopping-bound 1048576
.venv/bin/python verifier/verify_return9.py \
  artifacts/return9_certificate.json \
  --code-audit artifacts/return9_code_audit.json \
  --output artifacts/return9_verifier_result.json
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts --write artifacts/SHA256SUMS
```

## Tests

```text
137 passed in 50.79s
```

The Phase 4 tests cover the first-return formulas, code words, `n`/`z`
coordinates, exact family composition, the negative diagnostic cycles,
positive examples, all section integers below `2^24`, verifier acceptance, and
tamper rejection.

## Independent verifier

```json
{
  "closed_records": 10335,
  "direct_audit": {
    "bound_exclusive": 16777216,
    "section_integers_checked": 1864135,
    "sha256": "4185d73b4301ebc29c39bb7ba7e141ed6907d2580456ceb30bb10cea5f8a5d54",
    "shortcut_steps_checked": 7340021
  },
  "max_a": 8,
  "max_return_depth": 3,
  "open_records": 23785,
  "proves_collatz": false,
  "records": 34788,
  "return_code_kraft": "1/1",
  "return_code_prefix_free": true,
  "status": "verified_partial_return9_certificate_with_open_and_run_overflow",
  "templates": 52,
  "valid": true
}
```

The verifier is independent of `src/`. It reconstructs the automaton and
return formulas, code disjointness and exact Kraft sum, `z` identities,
compositions, recurrence bridges, closure inequalities, finite-tail witnesses,
and the full direct audit.

## Exact finite results and obstacles

- The direct audit checked all 1,864,135 integers `n = 2 (mod 9)` with
  `2 <= n < 2^24`, comprising 7,340,021 shortcut steps. Every first return
  agreed with the closed formula and the `z` coordinate.
- The exact infinite return code is prefix-free and has Kraft sum `1`.
- The finite dictionary has 52 templates (`a <= 8`). At return depth 3 it has
  33,696 cylinders, closes 9,911 at that level, and leaves 23,785 `OPEN`.
- The smallest exact unresolved family is
  `n(t)=47+18432*t`, with endpoint `155+59049*t` after three returns.
- The negative fixed point `-7` and cycle `-61 -> -34 -> -25 -> -61` are
  verified diagnostics only. They are not certificate closure rules.
- Positive examples include `11 -> 20`, `47 -> 182`, `83 -> 47`, and
  `128 -> 2` under first return to the section.
- Exact survivor growth is supercritical over the tested grid. The constants
  `1`, `5`, and `21` permit refill transitions under the tested ranking, so no
  global well-founded closure was obtained.
- First-return record scanning below `2^20` found nine record holders; the last
  is 1,031,807 with 41 returns before reaching the smaller section value
  908,606.

The full obstruction list is in `artifacts/return9_obstructions.json`; the
concise analysis is in `artifacts/phase4_obstruction_report.md`. All statements
above are exact finite or algebraic checks, not an asymptotic or universal
Collatz claim.

## Phase 4 SHA-256

```text
30dc1d5ff6b54ea50bd81f0d6e3be682fc1a2465df988514fa827829b3025630  mod27_dangerous_cycles.json
e3484f404cdcda28cbf4de82a74242b1360884bafcccaf43133187a9ef3f43d4  phase4_obstruction_report.md
e2db859379aefc47d87b4212943f6a85b8294964ac44a706c6ce128c1f2b9b37  return9_certificate.json
5a8d71cffe2e57130b51f503b22bf645aebc0a9b830238ccac47fa4933a7817a  return9_code_audit.json
1cf27f91a0c3b4ac61bb3a0c4656bf255c01a88dc2fd21a4b4b85811a635d24b  return9_obstructions.json
acb5d23906f3cddbdc36037653126b60d990d048e0dfdbd1c1a48bb474ecb291  return9_record_stopping_times.csv
8da2910fcedfad0a50e1b15ac64a4d504b99b708afa62b0ec9b2c5e4d37c146a  return9_survivors.csv
c939d16daab8068e79b162642e8036a5edaf45972a5c1207906d0f9504965464  return9_verifier_result.json
```

The complete manifest is `artifacts/SHA256SUMS`; its own SHA-256 is
`4304a81eee3f9ed3d832d81bc2b15e1bea5d314f9a8b0b25c03688ab9e596fc3`.
