# Phase 26 obstruction report

## Exact finite audit

- positive-D cyclic exponent classes through `q<=8`: `2214`;
- primitive classes: `2186`;
- noncoprime classes: `1417`;
- cyclic factor-width checks: `45369`;
- positive rational odd-height checks: `2214`.

These are bounded structural checks, not a search proving that all integer
cycles have been enumerated.

## Exact obstruction to the next critical area

The Phase 26 scalar argument excludes `A_*<=5`, but at `A_*=6` its
exponential comparison reverses:

```text
75^7 = 13348388671875
3*64^7 = 13194139533312
75^7 > 3*64^7
```

Thus EXT05 plus factor separation alone cannot exclude critical area six.
This does not construct an area-six cycle.  Critical area six is the first
remaining periodic target.

## What this result does not prove

Phase 26 does not eliminate all positive cycles, nonperiodic counterexamples,
or the Collatz conjecture. `proves_collatz=false`.
