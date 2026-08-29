# Scoped AI context packs

These files minimize context loading for one proof obligation. They do not
replace the claims ledger, Phase result reports, or mathematical proofs.

Before acting on a pack, an AI must run `scripts/research_health.py`, confirm
the referenced claim statuses, and read any directly linked counterexamples.
If a pack conflicts with `CLAIMS_LEDGER.md`, stop and repair the documentation
before research continues.

Each pack is intentionally short and records:

- the exact target and Collatz implication boundary;
- required dependencies;
- falsifiers that must survive;
- a useful first experiment;
- acceptance and stop conditions.

Current primary packs: [`H54.md`](H54.md), [`H70.md`](H70.md),
[`H72.md`](H72.md), [`H89.md`](H89.md), [`H104.md`](H104.md),
[`H105.md`](H105.md), and [`H133.md`](H133.md).
