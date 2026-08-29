# Phase 22 provenance

- Proposal audited: `phase22_cycle_resultant_note.md` (user-supplied untrusted
  local input; the proposal itself is not committed).
- Repository base: Phase 21 accepted `main` at
  `482f0357ffc5082e228bc4f3441b0a9e22f4f975`.
- Working branch: `feat/phase22-cycle-resultant`.
- Primary external sources checked: arXiv:2607.24844v1,
  DOI `10.1016/j.disc.2025.114812`, arXiv:2502.00948v5.
- Generator resultant: multiplication matrix in `Z[X]/(X^q-2)`.
- Verifier resultant: independently written Sylvester determinant.
- Exact finite scopes: all exponent compositions through `q=8`; all valid
  coprime profiles through `q=22` with defect area at most two.
- Floating point: not used for any proof or certificate decision.
- Collatz status: `OPEN`; `proves_collatz=false`.

Final commands, timings, commit, verifier result, and manifest digest are
recorded in `PHASE22_RUN_RESULTS.md` and the accepted experiment manifest.
