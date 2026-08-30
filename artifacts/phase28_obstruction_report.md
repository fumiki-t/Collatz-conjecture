# Phase 28 obstruction report

## NG37: finite strictness overstatement

For `q=3`, `L=5`, `e=(3,1,1)`, the reduced profile has
`A=J=h=1`, `delta=2/3`, and descent-floor sum zero.  Therefore both the new
finite bound and the triangular bound equal one.  The asymptotic leading
coefficient in P167/P168 remains stronger.

## NG38: missing `X^q=2` endpoint cost

For `q=2`, `L=4`, `e=(3,1)`, the profile `(0,1,0)` gives
`Q_a=(3,-1)` and `||Q_a||_1=4`, while the proposed bound is three.  The
corrected P171 bound adds `2^a_(q-1)-1=1`.  The endpoint-binomial
decomposition and support bound `<=2J+1` survive.

## Surviving structural regimes

The exact synthetic corpus contains `5` legal profiles:
one tall excursion, a long plateau with `A` much larger than `J`, isolated
unit excursions, a near-frontier mixed profile, and the Phase 25 seven-grid
control.  They are not integer cycles.

## Rotation boundary

NG36 remains active.  P133's least-value rotation and P156's discrepancy
minimum cannot be identified from rational-shadow algebra alone.  P166--P171
are stated in reduced-profile coordinates; any ordinary-source application
must transport rotations explicitly.

## First open obstruction

The corpus contains 2214 exact cyclic classes,
but no theorem turns near-extremal `h,J,A` saturation or the multilevel
endpoint polynomial into an all-area nonzero resultant.  This is H172.

## What this result does not prove

Phase 28 does not exclude arbitrary-area positive cycles, either nonperiodic
counterexample branch, or the Collatz conjecture. `proves_collatz=false`.
