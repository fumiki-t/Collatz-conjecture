# Adaptive affine Collatz certificates — Phase 1–4

This repository implements Phase 1–4 across the successive research briefs.
It is a finite exact search and obstruction-mining experiment. It does **not**
prove the Collatz conjecture.

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

## Phase 3 mixed-modulus search

Phase 3 adds coefficient-only structure auditing, mixed `LatticeNode`
binary/ternary splits, bounded exact `REVERSE_MERGE`, an independent verifier,
and an exact boundary-gap audit through boundary depth 36. It still produces a
large unresolved `OPEN` frontier and does not prove the Collatz conjecture.

```bash
.venv/bin/python -m pytest -q
.venv/bin/python src/phase3_search.py \
  --phase1-certificate artifacts/baseline_certificate.json \
  --binary-depth 20 --max-ternary 2 --boundary-depth 36
.venv/bin/python verifier/verify_phase3.py artifacts/phase3_certificate.json \
  --phase1-certificate artifacts/baseline_certificate.json \
  --output artifacts/phase3_verifier_result.json
.venv/bin/python scripts/hash_artifacts.py artifacts --write artifacts/SHA256SUMS
```

See `PHASE3_RUN_RESULTS.md` and `artifacts/phase3_obstruction_report.md` for the
checked result and the remaining exact bounded-search obstruction.

## Phase 4 exact mod-9 first-return search

Phase 4 works on the section `S = {n : n = 2 (mod 9)}`. It implements the
exact prefix-free first-return code, its `z=(4n+1)/3` parametrization, exact
composition through three returns, the recurrence constants `1`, `5`, and
`21`, and a separate verifier that imports no code from `src/`. The configured
finite dictionary leaves both an explicit `OPEN` frontier and all code families
with `a > 8` out of scope; neither is silently treated as closed.

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

See `PHASE4_RUN_RESULTS.md` and `artifacts/phase4_obstruction_report.md` for the
independently checked finite result, failed ranking proposals, and exact open
families. As in earlier phases, these results do not prove the Collatz
conjecture.

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
