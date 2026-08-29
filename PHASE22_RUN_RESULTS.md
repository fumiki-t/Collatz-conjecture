# Phase 22: cycle slope profiles and resultants — run results

Branch: `feat/phase22-cycle-resultant`

Base: `482f0357ffc5082e228bc4f3441b0a9e22f4f975`

Acceptance evidence commit: `b1aa7f0f67887df9230e213819d9259cf4182a4c`

Repository status: `OPEN`; `proves_collatz=false`.

## Accepted scope

The supplied note was audited as an untrusted proposal. Proofs, scope repairs,
and dependency boundaries are in
[`research/audits/cycle-resultant/REPORT.md`](research/audits/cycle-resultant/REPORT.md).

| Claim | Status | Accepted statement |
|---|---|---|
| EXT15 | `EXTERNAL_THEOREM` | Fernández--Ibáñez's exact swap and Christoffel `C_min` extremality are used only by P139. |
| EXT16 | `EXTERNAL_THEOREM` | Knight's high-cycle theorem is overlap/terminology context, not an all-cycle exclusion. |
| P133 | `VERIFIED_THEOREM` | Every primitive positive cycle minimum has a strict coefficient valley and `m(1-lambda)<q/3`. |
| P134 | `VERIFIED_THEOREM` | Every nontrivial primitive positive cycle is G170 critical-length or has `q>170m`. |
| P135/P136 | `VERIFIED_THEOREM` | Coprime classes have exact residue-indexed profiles and a slope-root congruence; area zero gives only the trivial cycle. |
| P137 | `VERIFIED_THEOREM` | Integral coprime profiles have nonzero resultant divisible by `D`, bounded above by radial energy. |
| P138 | `VERIFIED_THEOREM` | Every positive coprime area-one profile is excluded; EXT05 is isolated to the critical large-`q` part. |
| P139 | `CONDITIONAL` | EXT15 gives the quantitative non-Christoffel gap `g>3^(q-1)/4`. |
| P140 | `VERIFIED_THEOREM` | Noncoprime slopes obey a weaker grouped polynomial/resultant condition modulo `D_0`. |
| E34 | `VERIFIED_FINITE` | Exact composition/profile/resultant and adversarial audits in the declared bounds. |
| H133 | `OPEN` | Arbitrary-area coprime and general noncoprime positive cycles remain. |

## Finite results

- Full scope: all 16,623 positive exponent compositions and 2,214 cyclic
  classes for `q<=8`, `q<L<=2q`, `D>0`.
- Coprime/noncoprime classes: 797 / 1,417.
- Integral classes: only the trivial cycle and its nonprimitive powers.
- Area scope: all 4,786 valid coprime profiles with area at most two through
  `q<=22`—63 area zero, 670 area one, and 4,053 area two.
- Exact source exclusion: all 4,786 rows satisfy `C_min<300000D`.
- Exact radial-energy exclusion: 62 area-zero, 667 area-one, and 3,841
  area-two rows.
- Resultants: all 797 exhaustive coprime classes plus 512 deterministic
  larger-scope profiles—1,309 total—agree between the generator's
  multiplication matrix and the verifier's Sylvester determinant.
- Regressions: the trivial positive cycle, two named negative cycles, 30 word
  controls (including A/B, macro id0, NG28, and NG30), and 22 numeric family
  controls.

The zero finite survivor count is bounded evidence, not an all-area theorem.

## Reproduction

```bash
.venv/bin/python src/phase22_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase22.py \
  --artifact-dir artifacts --write-report artifacts/phase22_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase22_properties.py tests/test_phase22_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

Observed acceptance results:

- generator: `valid=true` in `4.82s` wall time;
- independent verifier: `valid=true` in `7.69s` wall time;
- property/tamper tests: `10 passed` in the initial focused run;
- focused Phase 22/control-plane tests: `15 passed in 31.47s`;
- full repository suite: `321 passed in 699.59s`;
- strict research health: `valid=true`, 146 tracked artifacts, no warnings;
- SHA-256 manifest: `b8be33ca4ce5f7c64900b0204cf09c67ccaf882e24eea4daca41a4ab14e32351`;
- independent result: `valid=true`, `proves_collatz=false`.

Final timings, commit, and manifest provenance are recorded in
`research/experiments/phase22-cycle-resultant.json` after acceptance.

## Tamper rejection

Tests reject:

- changing a stored resultant away from the independently rebuilt Sylvester
  determinant;
- changing the `D=-139` negative-cycle integral source;
- setting `proves_collatz=true`;
- importing the search implementation into the verifier.

## What this result does not prove

- The area-at-most-two audit is not an arbitrary-area theorem.
- P140 is not a full-`D` noncoprime exclusion.
- EXT15's Christoffel gap is conditional and insufficient alone.
- Positive nontrivial cycles, H133, H89, H112, H72, and the Collatz
  conjecture remain open.
- `proves_collatz=false`.
