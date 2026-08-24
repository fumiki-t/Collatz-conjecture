# Phase 11 obstruction report

This report does not claim a proof or disproof of the Collatz conjecture.

## Exact finite barrier audit

- Failure q values: [17, 22, 27, 29, 32, 34].
- Every failure has least pair (27,31) and gap 4.
- Every 35<=q<=4961 passes in the audited finite height.
- The first structurally vacuous q is 141; later finite passes do not contain a dropping-safe point once K_q reaches the scanned maximum dropping time.

## Height-free no-go

For every k>=3, 2^k-5 and 2^k-1 are k-step dropping-safe and have gap 4. Any spacing strategy that discards ordinary height is therefore refuted.

## Pair-cylinder result

- 16775072 pairs are represented by 262144 exact affine cylinders.
- The exact interval rule finds 48822 dropping-safe pairs at depth 12.
- This is a genuine endpoint-dominance/interval-closure rule, but it retains all 2^L residue classes and does not close the eventual target.
- NG19 prevents silently truncating those residue classes at L=12.

## What this result does not prove

Phase 11 does not prove the eventual dropping-safe barrier, eliminate nontrivial cycles, eliminate infinite coefficient-safe tails, prove C04/C05/H54, or prove the Collatz conjecture.
