# Phase 36 obstruction report

The proposed cycle-root localization is valid for reduced cycle profiles, but
its direct reuse after P206 has the wrong sign.  At `q=3` the safe
positions `[0, 1, 2]` decode to profile `[0, 0, 1]`.
The changed binary positions are `[2, 3]`; the naive
cycle interval `[[2, 3, 3, 5]]` misses one, while the corrected
mirror interval `[[2, 3, 2, 5]]` contains both.  This is NG42.

The exact NG41 area-229 scalar row is removed for a different reason. P208
forces `E=92=h+Sigma`, so every level-one cycle root has label length at most
two and binary span at most four. The only legal height-two root profiles are
`[1]`, `[1,1]`, and `[2,1]`. P212 then gives `6017`
against `2L=7294`. The complete area-229 frontier
therefore raises the accepted critical floor only to `A>=230`.

## What this result does not prove

It does not close the root-sparse/root-dense dichotomy, exclude arbitrary-area
cycles, turn decoder roots into smaller positive ancestors, close H89/H133/
H172, or prove Collatz. `proves_collatz=false`.
