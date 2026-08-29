# Phase 22 obstruction report

## Exact finite boundary

The audit exhausts every positive exponent composition through `q<=8` and
every valid coprime profile with area at most two through `q<=22`.  The second
scope is area-bounded, not a full composition search.

- exhaustive cyclic classes: `2214`;
- area-bounded valid profiles: `4786`;
- area counts: `{"0": {"combined_excluded": 63, "energy_excluded": 62, "integral": 1, "source_excluded": 63, "uncovered": 0, "valid": 63}, "1": {"combined_excluded": 670, "energy_excluded": 667, "integral": 0, "source_excluded": 670, "uncovered": 0, "valid": 670}, "2": {"combined_excluded": 4053, "energy_excluded": 3841, "integral": 0, "source_excluded": 4053, "uncovered": 0, "valid": 4053}}`;
- combined energy/source survivors: `0`.

## Smallest surviving obstruction

`none in the declared finite scope`

The row fields are `q,L,profile,exponents,area,B,D,D|B,C_min,source_excluded,
energy_excluded,energy_upper_numerator,energy_upper_denominator`.  A survivor is
not a cycle: it only survives these two necessary-condition filters.  Exact
integrality and literal legality remain separate.

## Missing bridge

The resultant divisibility and energy inequality require a uniform lower bound
on profile roughness, or an alternative source bound, for arbitrary defect
area.  P140 supplies only a weaker modulus for noncoprime slopes.  Neither
finite coverage nor the Christoffel extremal theorem provides this bridge.

## What this result does not prove

It does not eliminate all positive nontrivial cycles, H89, H112, H72, or prove
the Collatz conjecture.  `proves_collatz=false`.
