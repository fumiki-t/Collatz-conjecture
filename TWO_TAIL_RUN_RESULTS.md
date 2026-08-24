# Two-tail finite-state supplement: run results

Branch: `research/two-tail-state-collisions`

Base commit: `5cf5a0197ea206104be12d8afaa51c9e6e5d0b0a`

This supplement follows the Phase 10 branch-point decomposition and tests a
precise continuation state for C05. It proves one finite-horizon arithmetic
lemma, refutes every literal shortened-residue version at horizon 12, and
preserves the minimal exact collisions. It does not prove or disprove the
Collatz conjecture. `proves_collatz=false`.

## Reproduction commands

```bash
.venv/bin/python src/two_tail_search.py \
  --artifact-dir artifacts --bound 20000 --gap-cap 512 --horizon 12
.venv/bin/python verifier/verify_two_tail.py \
  --artifact-dir artifacts --output artifacts/two_tail_verifier.json
.venv/bin/python -m pytest -q tests/test_two_tail_properties.py \
  tests/test_two_tail_verifier.py tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
.venv/bin/python scripts/research_health.py
shasum -a 256 artifacts/SHA256SUMS
```

The independent verifier does not import `src/two_tail_search.py`. It rebuilds
the coefficient-loss depths, common prefixes, odd transformed gaps, both tail
words, collision minimality order, eligible-pair count, dependency hash, and
mandatory adversarial digest. Stored derived values are not trusted.

## P68 — exact finite-horizon two-tail state (`VERIFIED_THEOREM`)

Let `n<m`, `h=v2(m-n)`, and suppose their shared prefix is coefficient-safe
through h. Write

```text
a = number of odd steps in the common prefix,
u = (m-n)/2^h,
y = T^h(n).
```

By P66 the other tail begins at `y+3^a u`, and `3^a u` is odd. For any finite
`L>=1`, the state

```text
(h, a, u, branch orientation, y mod 2^L)
```

determines both tails' next-L parity words. Indeed, a length-L parity word is
determined by its initial residue modulo `2^L`, and the second residue is
`y+3^a u mod 2^L`. If the first j new bits contain `c_j` odd steps, the exact
coefficient at that point is

```text
3^(a+c_j) / 2^(h+j).
```

Thus every coefficient-safety comparison during those next L steps is also
determined using integer arithmetic. The theorem assumes safety through the
common prefix; it does not reconstruct the internal order of the earlier h
bits from `(h,a)` alone.

## NG19 — shortened residue windows (`REFUTED`)

At `L=12`, the tested hypothesis was that some `b<L` in

```text
(h, a, u, orientation, y mod 2^b)
```

still decides whether both tails remain coefficient-safe through all 12 new
steps. The production scan refutes every `b=0,...,11`. Pairs are enumerated in
increasing upper endpoint and then increasing positive difference, so each row
is the first collision for that width in the declared scan.

| b | first pair | outcome | second pair | outcome | compressed state |
|---:|---:|:---:|---:|:---:|---|
| 0 | `(3,7)` | no | `(27,31)` | yes | `(2,2,1,01,0)` |
| 1 | `(3,7)` | no | `(27,31)` | yes | `(2,2,1,01,0)` |
| 2 | `(11,15)` | no | `(27,31)` | yes | `(2,2,1,01,2)` |
| 3 | `(27,31)` | yes | `(59,63)` | no | `(2,2,1,01,6)` |
| 4 | `(7,27)` | no | `(71,91)` | yes | `(2,2,5,10,1)` |
| 5 | `(27,39)` | no | `(155,167)` | yes | `(2,2,3,01,30)` |
| 6 | `(27,31)` | yes | `(283,287)` | no | `(2,2,1,01,62)` |
| 7 | `(27,31)` | yes | `(539,543)` | no | `(2,2,1,01,62)` |
| 8 | `(27,47)` | yes | `(1051,1071)` | no | `(2,2,5,01,62)` |
| 9 | `(47,239)` | yes | `(991,1183)` | no | `(6,5,3,01,182)` |
| 10 | `(27,63)` | yes | `(4123,4159)` | no | `(2,2,9,01,62)` |
| 11 | `(1407,1663)` | yes | `(15551,15807)` | no | `(8,7,1,01,1788)` |

This is a genuine counterexample family, not a heuristic ranking failure. It
rules out the whole specified fixed-truncation mechanism at L=12. The surviving
weaker statement is exactly P68 with `b=L`.

## E17 — production finite audit (`VERIFIED_FINITE`)

The exact bounds are:

```text
2 <= n < m <= 20,000
m-n <= 512
L = 12
eligible pairs = 6,887,319
stored minimal collisions = 12
```

A pair is eligible when its common branch prefix is coefficient-safe. The
acceptance decision uses arbitrary-precision integer comparisons only. The
audit also reconstructs 5,156 adjacent pairs from the mandatory families:

```text
2^m-1, 1<=m<=64
8^m-5, 1<=m<=32
all 4096 twelve-block (110|111)^* inverse-parity residues
A=11101, B=1100
A^rB^s, 1<=r,s<=32
```

## Obstruction and next research step

The exact L-bit window is lossless but grows linearly with the requested
horizon. Removing any one or more high bits without additional structure is
unsound at L=12. A scalable C05 certificate must instead do at least one of:

- propagate exact carry intervals/cylinders compositionally;
- prove a sound dominance relation that merges histories with identical future
  obligations;
- derive an ordinary-size lower bound from `(h,a,u)` plus a recursive residue
  constraint;
- explicitly separate all stored NG19 collisions before attempting q0 scale.

Extending H or L with the same state format would provide more finite evidence
but no asymptotic mechanism.

## Tamper rejection

Tests alter and require rejection of:

- the P68 theorem boundary;
- the NG19 status;
- a stored minimal collision witness;
- the mandatory adversarial digest;
- the C05 status.

The test suite also checks that the verifier does not import the search module.

## What this result does not prove

This supplement does not prove that every possible unbounded state compression
fails. It does not prove C04, C05, H54, H57, the existence or nonexistence of a
least counterexample, or the Collatz conjecture. A bounded absence or presence
of collisions cannot be promoted to an asymptotic statement. The target
`Delta_(K0-1)(2^72)>W` was not evaluated.

## Acceptance result and SHA-256

Acceptance result: `188 passed in 269.84s`. The focused supplement and health
suite result is `5 passed in 3.88s`. The committed independent result
records `valid=true`, C05 as `OPEN`, and `proves_collatz=false`.

```text
4fe9acbec6dafcf394c18e9fe84a007b262f9ea2a09832ef636f72810ea6a3ef  two_tail_state_collisions.json
cad55a1aaff164762595e9c1b5dbced6659593f4514a9de812aced49a07c2a3b  two_tail_verifier.json
```

SHA-256 of `artifacts/SHA256SUMS`:
`79ebbb612a5496c7d97247b99450bfb8582a1b7bff01957890d0075af8b2de25`.
