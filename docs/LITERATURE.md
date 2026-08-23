# Annotated literature

**Metadata last checked:** 2026-08-23. Links below point to publishers, DOI
records, author-hosted copies, or arXiv. An `EXTERNAL_THEOREM` label means the
result is external to this repository; it does not mean its proof has been
independently reproduced here.

## Foundational and structural

### Terras (1976)

**Status:** `EXTERNAL_THEOREM`

Riho Terras, “A stopping time problem on the positive integers,” *Acta
Arithmetica* **30**(3) (1976), 241–252.
[DOI 10.4064/aa-30-3-241-252](https://doi.org/10.4064/aa-30-3-241-252).

**Result relevant here.** Classical stopping/coefficient-stopping and parity
residue structure underlying the coefficient-safe language.

**Repository role.** Phase 6 safe-prefix counting is the classical
unconverged/admissible parity-vector count in complementary notation. Phase 7
does not claim this language or its counts as new.

### Bernstein and Lagarias (1996)

**Status:** `EXTERNAL_THEOREM`

D. J. Bernstein and J. C. Lagarias, “The 3x + 1 Conjugacy Map,” *Canadian
Journal of Mathematics* **48** (1996), 1154–1169.
[DOI 10.4153/CJM-1996-060-x](https://doi.org/10.4153/CJM-1996-060-x).

**Result relevant here.** The 2-adic parity-vector/conjugacy framework and the
unique reconstruction of a 2-adic integer from its parity vector.

**Repository role.** Structural background for affine cylinders and parity
words. Current finite certificates reconstruct their own arithmetic and do not
delegate acceptance to this paper.

### Garner (1981)

**Status:** `EXTERNAL_THEOREM`

Lynn E. Garner, “On the Collatz 3n + 1 Algorithm,” *Proceedings of the
American Mathematical Society* **82**(1) (1981), 19–22.
[DOI 10.1090/S0002-9939-1981-0603593-2](https://doi.org/10.1090/S0002-9939-1981-0603593-2).

**Result relevant here.** Historical cycle-length constraints obtained from
relations between powers of 2 and 3.

**Repository role.** Context only; it is not an input to the Phase 6 finite
certificates.

### Krasikov and Lagarias (2003)

**Status:** `EXTERNAL_THEOREM`

Ilia Krasikov and Jeffrey C. Lagarias, “Bounds for the 3x+1 Problem Using
Difference Inequalities,” *Acta Arithmetica* **109**(3) (2003), 237–258.
[DOI 10.4064/aa109-3-4](https://doi.org/10.4064/aa109-3-4),
[arXiv:math/0205002](https://arxiv.org/abs/math/0205002).

**Result relevant here.** Computer-aided difference inequalities give a lower
bound of at least `x^0.84` integers below `x` whose orbit contains 1.

**Repository role.** Context for predecessor/density approaches. The result
does not control a single hypothetical exceptional least counterexample, so it
does not repair NG12 by itself.

## Sufficient sets and modular dynamics

### Monks, Monks, Monks, and Monks (2013; arXiv 2012)

**Status:** `EXTERNAL_THEOREM`

Keenan Monks, Kenneth G. Monks, Kenneth M. Monks, and Maria Monks, “Strongly
sufficient sets and the distribution of arithmetic sequences in the 3x+1
graph,” *Discrete Mathematics* **313**(4) (2013), 468–489.
[DOI 10.1016/j.disc.2012.11.019](https://doi.org/10.1016/j.disc.2012.11.019),
[arXiv:1204.3904](https://arxiv.org/abs/1204.3904).

**Result relevant here.** Every positive forward orbit meets `2 mod 9`; every
nontrivial cycle and divergent orbit meets `20 mod 27`.

**Repository role.** External justification for the Phase 4 mod-9 section and
the Phase 5 mod-27 section strategy. The repository independently verifies its
finite return dictionaries, not the global strongly-sufficient theorem.

## Parity vectors and critical density

### López and Stoll (2009)

**Status:** `EXTERNAL_THEOREM`

Josefina López and Peter Stoll, “The 3x + 1 Conjugacy Map over a Sturmian
Word,” *Integers* **9**(2) (2009), 141–162.
[DOI 10.1515/INTEG.2009.014](https://doi.org/10.1515/INTEG.2009.014).

**Result relevant here.** The 2-adic conjugacy map over mechanical/Sturmian
parity words, including continued-fraction structure in that low-complexity
class.

**Repository role.** Context and adversarial model only. A hypothetical
critical trajectory is not known to be Sturmian, so this cannot be used as a
full reduction.

### López and Stoll (2021)

**Status:** `EXTERNAL_THEOREM` from a preprint, not an active proof dependency

Josefina López and Peter Stoll, “The 3x+1 Periodicity Conjeture in
`R`,” arXiv:2101.12747 (2021).
[arXiv:2101.12747](https://arxiv.org/abs/2101.12747).

The spelling “Conjeture” is the title recorded by arXiv.

**Result relevant here.** The authors state that a rational 2-adic integer
with a noncyclic trajectory must have lower limiting parity-one density
`ln(2)/ln(3)`.

**Repository role.** Context for the critical density. Before this result is
made a proof dependency, a human specialist should audit the precise map,
notion of rationality, and quantifiers against this repository's positive
integer setting.

## Almost-everywhere results

### Tao (2022)

**Status:** `EXTERNAL_THEOREM`

Terence Tao, “Almost all orbits of the Collatz map attain almost bounded
values,” *Forum of Mathematics, Pi* **10** (2022), e12, 1–56.
[DOI 10.1017/fmp.2022.8](https://doi.org/10.1017/fmp.2022.8),
[arXiv:1909.03562](https://arxiv.org/abs/1909.03562).

**Result relevant here.** For every function tending to infinity, the minimum
orbit value is below that function for almost all starting integers in
logarithmic density.

**Repository role.** Essential context and a warning: “almost all” does not
exclude one hypothetical least counterexample. The theorem is not used by any
current certificate.

## Coefficient stopping and paradoxical behavior

### Rozier and Terracol (2026; first posted 2025)

**Status:** `EXTERNAL_THEOREM`; publication metadata updated from the original
research draft

Olivier Rozier and Claude Terracol, “Paradoxical behavior in Collatz
sequences,” *Discrete Mathematics* **349** (2026), 115167.
[DOI 10.1016/j.disc.2026.115167](https://doi.org/10.1016/j.disc.2026.115167),
[arXiv:2502.00948](https://arxiv.org/abs/2502.00948) (initial submission 2025;
version 5 dated 2026-05-17).

**Result relevant here.** Connections among coefficient stopping, finite
paradoxical sequences, and the Collatz conjecture. Phase 8 uses the exact
statement of Lemma B.1: for positive `k,q` with `q>12`,
`|2^k-3^q|>(64/25)^q/2`.

**Repository role.** Motivation for the critical-prefix language. The paper's
empirical suggestion of finiteness is not imported as a theorem, and it is not
an input to Phase 6 certificates. Phase 7 records substantial overlap with its
paradoxical-sequence and continued-fraction setting. Phase 8 isolates Lemma
B.1 as EXT05 and applies it only with exponent `q>=30`; therefore the C02 proof
does not use the paper's separate finite check for `13<=q<=18`.

### Ellison (1971)

**Status:** `EXTERNAL_THEOREM`; indirect dependency through EXT05

W. J. Ellison, “On a theorem of S. Sivasankaranarayana Pillai,” *Séminaire de
Théorie des Nombres de Bordeaux* (1971), 1–10.

**Result relevant here.** Rozier--Terracol derive the `q>18` part of Lemma B.1
from their cited form of Ellison's Theorem 3.

**Repository role.** The repository does not independently rederive
Rozier--Terracol's reduction or Ellison's theorem. It records this dependency
chain explicitly; Phase 8 verifies only that its own exponents lie in the
`q>=30` regime and that the subsequent rational inequalities are exact.

### Niu (2026; withdrawn)

**Status:** `RETRACTED` as a source; not used as mathematical authority

Tong Niu, “Parity vectors and paradoxical sequences in the accelerated Collatz
map,” arXiv:2605.13886v2 (2026).
[arXiv:2605.13886](https://arxiv.org/abs/2605.13886).

**Result relevant here.** The note discussed parity-vector counts and the
continued-fraction/Stern--Brocot structure of the seven paradoxical `(j,q)`
pairs.

**Repository role.** The author withdrew v2 because Rozier--Terracol v4 had
already enumerated the 593 sequences and seven pairs. It is retained only as
an overlap warning and supplies no proof dependency.

### Hikawa (2026 preprint)

**Status:** `EXTERNAL_EVIDENCE`; preprint, not an active proof dependency

Kazunobu Hikawa, “Finite-Dimensional Combinatorial and Arithmetic Structures
of Parity Vectors for the Accelerated Collatz Map,” ResearchGate preprint,
July 2026, DOI 10.13140/RG.2.2.29894.84804.

**Result relevant here.** Finite-dimensional parity-vector counting and
arithmetic rigidity, with explicit links to OEIS A100982 and A076227.

**Repository role.** Phase 7 independently rederives its fixed-`(k,q)` residue
rigidity. The preprint documents prior overlap; it is not used to accept the
repository theorem.

### OEIS A100982 and A076227

**Status:** `EXTERNAL_EVIDENCE`

- [A100982](https://oeis.org/A100982): admissible-sequence counts by odd-step
  order.
- [A076227](https://oeis.org/A076227): surviving coefficient-safe residues by
  prefix length.

**Repository role.** A076227 exactly matches the Phase 1/6 safe-prefix counts,
including `a(26)=1037374`. Phase 7 reproduces selected A100982 terms
`1,2,7,312455` at `q=1,3,5,17`. The internally verified enumerations do not
depend on OEIS, and the known sequence identities limit the newness claim.

## Rotation sums

### Denjoy--Koksma inequality

**Status:** `EXTERNAL_THEOREM`

L. Kuipers and H. Niederreiter, *Uniform Distribution of Sequences*,
Wiley-Interscience, 1974, Chapter 2; classical Denjoy--Koksma inequality for
bounded-variation functions at continued-fraction denominators.

**Result relevant here.** For an irrational circle rotation and a
bounded-variation function, the denominator-length Birkhoff sum differs from
its mean by at most the total variation.

**Repository role.** Phase 7 checks the exact continued-fraction denominators,
decomposition, integrals, and variations, but does not reprove the theorem.
It is the only `EXTERNAL_MATH_INPUT` used to turn boundary-defect pressure into
explicit contact and autocorrelation bounds.

## Diophantine approximation

### Wu and Wang (2014)

**Status:** `EXTERNAL_THEOREM`

Qiang Wu and Lihong Wang, “On the irrationality measure of `log 3`,” *Journal
of Number Theory* **142** (2014), 264–273.
[DOI 10.1016/j.jnt.2014.03.007](https://doi.org/10.1016/j.jnt.2014.03.007).

**Result relevant here.** An effective irrationality-measure estimate for
`log 3`, hence linear-form control involving powers of 2 and 3 after the needed
conversion.

**Repository role.** Context for the approximate upper bound
`H_q = O(q^5.117)`. Neither the paper's proof nor the conversion with explicit
constants is audited here. The bound is not an input to a current finite
certificate.

## Human-verification queue

Bibliographic metadata above was checked against primary records. Before any
item becomes a dependency of a claimed Collatz proof, human mathematical audit
is still required for:

1. the exact López–Stoll (2021) quantifiers and transfer from rational 2-adics
   to the positive-integer least-counterexample setting;
2. the derivation, exponent rounding, and effective constants in converting
   Wu–Wang to the contextual `H_q = O(q^5.117)` statement;
3. the complete proof chain from Ellison's Theorem 3 to Rozier--Terracol Lemma
   B.1 if EXT05 ever becomes part of a claimed full Collatz proof.
