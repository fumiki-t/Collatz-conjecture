# Adaptive affine Collatz certificates — Phase 1–2

This repository implements only Phase 1 and Phase 2 of
`collatz_codex_research_brief.md`. It is a finite exact search and obstruction
mining experiment. It does **not** prove the Collatz conjecture.

All certificate decisions use Python arbitrary-precision integers. Rational
fixed points use `fractions.Fraction`; floating point is not used for proof or
clustering decisions.

## What is implemented

- `src/model.py`: exact affine cylinders, exact splits, direct shortcut map,
  and repeated-block affine maps.
- `src/search.py`: deterministic depth-first Phase 1 search. It writes a valid
  streaming JSON document without retaining the multi-million-node tree in
  memory.
- `verifier/verify_certificate.py`: independent checker. It imports no search
  or model code and reconstructs every split, inequality, and direct witness.
- `src/mine_obstructions.py`: exact Phase 2 survivor statistics, repeated
  blocks of length at most 16, discrete signatures, and the failed-dictionary
  report.
- `tests/`: Hypothesis properties, sanity counts, tamper rejection, required
  adversarial families, and exact block checks.

Certificate records are compact arrays
`[k,r,y,q,parity_word,rule]`. `OPEN` is not a proof rule: it explicitly marks
the unresolved depth-limited frontier. `FINITE_TAIL` contains the exact high
parameter and one `[n, step_count, endpoint]` DIRECT witness per exception;
the verifier recomputes all intermediate orbit arithmetic.

## Reproduce

Python 3.12 or later is required. From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python src/search.py --depth 26 --output artifacts/baseline_certificate.json
.venv/bin/python verifier/verify_certificate.py artifacts/baseline_certificate.json
.venv/bin/python src/mine_obstructions.py --certificate artifacts/baseline_certificate.json
.venv/bin/python scripts/hash_artifacts.py artifacts --write artifacts/SHA256SUMS
```

The default search exhaustively compares every represented integer `n` with
`2 <= n < 2^24` against literal shortcut iteration. For a quick smoke test,
pass `--coverage-bound 4096`; that is not an acceptance run.

The checked acceptance-run outputs and hashes are recorded in
`RUN_RESULTS.md` and `artifacts/SHA256SUMS`.

## Interpretation boundaries

- **Proved by the checker:** the finite JSON tree is internally exact; every
  recorded SPLIT, DESCENT, FINITE_TAIL, and DIRECT rule is valid.
- **Observed computationally:** node counts, survivor counts, exact finite-depth
  block coverage, signatures, and counterexample words in the artifacts.
- **Conjectured/future work:** asymptotic growth behavior and whether a
  parametric MACRO plus well-founded MERGE dependencies can close the frontier.

The Phase 2 dictionary test calls a branch “explained” only when its prefix or
suffix contains at least three consecutive copies of a block of length at most
16. Requiring only two would vacuously label the common survivor prefix `11` as
an explanation. A failure refutes only this precise finite-depth dictionary
test; it is not a theorem ruling out other macro languages.
