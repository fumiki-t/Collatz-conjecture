# Annotated literature

**Metadata last checked:** 2026-08-27. Links below point to publishers, DOI
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

### Heppner (1978) and Garcia--Tal (1999)

**Status:** `EXTERNAL_THEOREM`; active conditional input EXT07

Ernst Heppner, “Eine Bemerkung zum Hasse--Syracuse-Algorithmus,”
*Archiv der Mathematik* **31** (1978), 317--320, MR 80d:10007.

Manuel V. P. Garcia and Fabio A. Tal, “A note on the generalized 3n+1
problem,” *Acta Arithmetica* **90**(3) (1999), 245--250.
[DOI 10.4064/aa-90-3-245-250](https://doi.org/10.4064/aa-90-3-245-250),
[publisher PDF](https://matwbn.icm.edu.pl/ksiazki/aa/aa90/aa9033.pdf).

**Result relevant here.** Garcia--Tal Proposition 1 quotes Heppner's
quantitative estimate for generalized Hasse maps when
`m<d^(d/(d-1))`. Their Fundamental Lemma and equation (6) then bound, uniformly
in the interval location, the number of equal-time collision-free
representatives in an interval. Corollary 1 gives zero Banach density.

For `d=2`, `m=3`, and `R={0,-1}`, the Hasse map is exactly the repository's
shortcut Collatz map. Equation (6), not merely the Banach-density corollary,
gives EXT07 with an unspecified `beta<1` and an orbit-dependent constant.

**Repository role.** The audit in
[`../research/audits/garcia-tal-phase12/REPORT.md`](../research/audits/garcia-tal-phase12/REPORT.md)
checks the specialization, interval quantifiers, and direct consequences.
The repository does not reprove Heppner's proposition. P74 and P75 are
therefore recorded as `CONDITIONAL`, and no numerical value of `beta` is
assumed.

### Bernstein and Lagarias (1996)

**Status:** `EXTERNAL_THEOREM`

D. J. Bernstein and J. C. Lagarias, “The 3x + 1 Conjugacy Map,” *Canadian
Journal of Mathematics* **48** (1996), 1154–1169.
[DOI 10.4153/CJM-1996-060-x](https://doi.org/10.4153/CJM-1996-060-x).

**Result relevant here.** The 2-adic parity-vector/conjugacy framework and the
unique reconstruction of a 2-adic integer from its parity vector.

**Repository role.** Structural background for affine cylinders, parity words,
and Phase 10 supplement P66's prefix-agreement criterion. P66 gives its own
finite integer/modulo-power proof and verifier; acceptance is not delegated to
this paper.

### Fernández and Ibáñez (2026 preprint)

**Status:** `EXTERNAL_THEOREM`; preprint, not an active proof dependency

Carlos Fernández and Santiago Ibáñez, “Christoffel words as extremal
structures in Collatz dynamics,” arXiv:2607.24844v1 (2026).
[arXiv:2607.24844](https://arxiv.org/abs/2607.24844).

**Result relevant here.** The authors report that, at fixed word length and
number of odd symbols, Christoffel words are, up to rotation, the unique
maximizers of their rotation-class functional `C_min`, and derive cycle
restrictions from that extremality.

**Repository role.** This is external context for Phase 10's formal
rational-cycle minimum lemma P65. Phase 10 proves its own prefix-minimum and
gcd identities directly and does not reprove or use Christoffel extremality to
accept any certificate. No novelty claim is made against the preprint.

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

### Stérin (2020; arXiv 2019)

**Status:** `EXTERNAL_THEOREM`; predecessor-language context, not a Phase 15
proof dependency

Tristan Stérin, “Binary expression of ancestors in the Collatz graph,” in
*Reachability Problems 2020*; [arXiv:1907.00775v4](https://arxiv.org/abs/1907.00775)
(submitted 2019, revised 2020; accepted at RP 2020).

**Result relevant here.** For a fixed budget `k` of odd shortcut steps, the
binary expressions of ancestors of a fixed integer form a regular language.
The paper constructs a regular expression in time exponential in `k` and
describes the associated binary carry propagation.

**Repository role.** Phase 15's finite cross-Q source/endpoint enumeration and
P88's `{1,2}`-gap backward residue decoder overlap the broad predecessor and
carry-language setting. The repository does not claim novelty for that finite
encoding. Stérin's result does not provide P86's least-source surplus theorem,
an ordinary-height anti-concentration estimate, or eventual extinction of the
H72 frontier, and it is not used to accept P86--P88 or E24.

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

### Lagarias (1985)

**Status:** `EXTERNAL_THEOREM`

Jeffrey C. Lagarias, “The 3x + 1 Problem and Its Generalizations,” *The
American Mathematical Monthly* **92**(1) (1985), 3–23.
[DOI 10.2307/2322189](https://doi.org/10.2307/2322189).

**Result relevant here.** Relation (2.31) records that an integer trajectory
tending to infinity has lower limiting parity-one density at least
`ln(2)/ln(3)`.

**Repository role.** This is direct prior overlap for critical parity density.
Phase 12 does not claim the density threshold as new and does not use the
external result to accept P72; its added statement packs distinct positive odd
orbit values and controls the octave defect `a_i`.

### Monks and Yazinski (2004)

**Status:** `EXTERNAL_THEOREM`

Kenneth G. Monks and Jonathan Yazinski, “The Autoconjugacy of the 3x + 1
Function,” *Discrete Mathematics* **275**(1–3) (2004), 219–236.
[DOI 10.1016/S0012-365X(03)00125-0](https://doi.org/10.1016/S0012-365X(03)00125-0),
[author-hosted manuscript](https://monks.scranton.edu/files/pubs/AutoConjV13.pdf).

**Result relevant here.** Theorem 2.7(b) extends the lower bound
`ln(2)/ln(3)` to the lower parity-one density of a divergent rational 2-adic
orbit.

**Repository role.** This extends the domain of the classical density
restriction. P72 is instead an internally proved positive-integer
odd-value-packing result and does not depend on the 2-adic theorem.

### López and Stoll (2009)

**Status:** `EXTERNAL_THEOREM`

Josefina López and Peter Stoll, “The 3x + 1 Conjugacy Map over a Sturmian
Word,” *Integers* **9**(2) (2009), 141–162.
[DOI 10.1515/INTEG.2009.014](https://doi.org/10.1515/INTEG.2009.014).

**Result relevant here.** The 2-adic conjugacy map over mechanical/Sturmian
parity words, including continued-fraction structure in that low-complexity
class.

**Repository role.** Context and adversarial model only. Phase 12 identifies
its all-contact word with the upper mechanical word of critical slope, but
proves positive-integer impossibility from P72 rather than importing a
Sturmian theorem. A hypothetical
critical trajectory is not known to be Sturmian, so this cannot be used as a
full reduction.

### López and Stoll (2021)

**Status:** `EXTERNAL_THEOREM`; active conditional input EXT08

Josefina López and Peter Stoll, “The 3x+1 Periodicity Conjeture in
`R`,” arXiv:2101.12747 (2021).
[arXiv:2101.12747](https://arxiv.org/abs/2101.12747).

The spelling “Conjeture” is the title recorded by arXiv.

**Result relevant here.** Theorem `aperiodic` states that a rational 2-adic
integer whose shortcut orbit is an infinite set has lower limiting parity-one
density `ln(2)/ln(3)`.

**Phase 20 audit.** The arXiv TeX source and proof were inspected rather than
only the abstract. The map is exactly `x/2` or `(3x+1)/2`, the counted bit is
the input parity, `Q_odd` is the rational 2-adic subring, and the conclusion is
`liminf`, not existence of a natural density. The proof separates the cases
`liminf` above and below the critical density.

**Repository role.** EXT08 is an explicit external input to P119/P121/P123/
P124. The repository does not reproduce the paper's real-conjugacy proof.
Positive integers lie in the rational 2-adics, but this input does not prove
that their orbits terminate; the cyclic branch remains separate.

## Word frequency and low complexity

### Allouche--Shallit and Saari

**Status:** `EXTERNAL_THEOREM`; EXT10

Jean-Paul Allouche and Jeffrey Shallit, *Automatic Sequences: Theory,
Applications, Generalizations*, Cambridge University Press, 2003,
Theorem 8.4.5.
[Cambridge book record](https://doi.org/10.1017/CBO9780511546563).

Kalle Saari, “On the Frequency of Letters in Pure Binary Morphic Sequences,”
*Developments in Language Theory 2005*, LNCS 3572, 397--408.
[DOI 10.1007/11505877_35](https://doi.org/10.1007/11505877_35).

**Result relevant here.** An existing morphic letter frequency is algebraic.
Saari separately proves that letter frequencies exist for every pure binary
morphic word, including the nonprimitive case.

**Repository role.** P119 uses algebraicity only after natural-frequency
existence has been supplied. General morphic words may lack natural frequency;
their logarithmic frequencies are not substituted.

### Bell (2020)

**Status:** `EXTERNAL_THEOREM`; EXT11

Jason P. Bell, “The upper density of an automatic set is rational,”
*Journal de théorie des nombres de Bordeaux* **32**(2) (2020), 585--604.
[DOI 10.5802/jtnb.1135](https://doi.org/10.5802/jtnb.1135).

**Result relevant here.** The lower and upper asymptotic densities of every
`k`-automatic set are recursively computable rational numbers.

**Repository role.** P119 compares the rational lower density of the set of
one positions with EXT08/P118. It does not assume that the automatic word has
a natural density.

### Cassaigne (1997/1998)

**Status:** `EXTERNAL_THEOREM`; EXT12

Julien Cassaigne, “Sequences with grouped factors,” *Developments in Language
Theory III* (conference 1997; proceedings 1998), 211--222.

**Result relevant here.** A quasi-Sturmian word is a finite prefix followed by
a morphic image `phi(s)` of a Sturmian word, with
`phi(ab)!=phi(ba)`. The latter condition forces both source-letter images to
be nonempty.

**Repository role.** P122 proves the required bounded output discrepancy
inside the repository. EXT12 is used only to transfer that calculation to all
quasi-Sturmian words in P123/P124.

### Primitive substitution frequencies

**Status:** `EXTERNAL_THEOREM`; EXT13

Martine Queffélec, *Substitution Dynamical Systems -- Spectral Analysis*,
second edition, Lecture Notes in Mathematics 1294, Springer, 2010.
[DOI 10.1007/978-3-642-11212-6](https://doi.org/10.1007/978-3-642-11212-6).

**Result relevant here.** A primitive substitution has letter frequencies
given by the normalized positive Perron eigenvector of its integral incidence
matrix. The eigenvalue and coordinates are algebraic.

**Repository role.** EXT13 supplies the primitive-substitutive subcase of
P119. No corresponding existence claim is made for arbitrary nonprimitive
substitutions.

### Gelfond--Schneider

**Status:** `EXTERNAL_THEOREM`; EXT09

The classical Gelfond--Schneider theorem states that if algebraic `alpha` is
neither zero nor one and algebraic `beta` is irrational, every value of
`alpha^beta` is transcendental. A standard authoritative reference is Serge
Lang, *Introduction to Transcendental Numbers*, Addison--Wesley, 1966,
Chapter I.

**Repository role.** P118 supplies the elementary irrationality argument and
applies the theorem only with `alpha=3`, `beta=ln(2)/ln(3)`, and positive real
value `2`.

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

### Angeltveit (2026 preprint)

**Status:** primary-source context; not an active external proof dependency

Vigleik Angeltveit, “An improved algorithm for checking the Collatz
conjecture for all `n < 2^N`,” arXiv:2602.10466 (2026).
[arXiv:2602.10466](https://arxiv.org/abs/2602.10466).

**Result relevant here.** Section 2.3, especially Lemmas 2.6--2.9, states
mod-3/mod-9 preimage sieves, a path-merging sieve, and the odd-even-even
sieve. Lemma 2.9 is attributed there to Christian Hercher's 2023 cycle paper.

**Repository role.** Phase 16 independently proves the exact shortcut-map
formulas used in P99 by literal traces and algebra. The paper establishes the
overlap/newness boundary and motivates a future merge automaton; it is not an
input to P99, P100, or P101. No algorithmic finite verification result from
the preprint is imported as evidence here.

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

Theorem 1.3 in arXiv v5 reports exactly 593 paradoxical sequences with initial
element at most 4,614 and proves that any additional one must start above
`2.8*10^19`; it also states the conditional implication that if no additional
paradoxical sequence exists, then Collatz is true. The stronger assertion that
there is no sequence above 4,614 is presented by the authors as a
heuristic/conjectural conclusion, not as the theorem.

**Repository role.** Motivation for the critical-prefix language. The paper's
empirical suggestion of finiteness is not imported as a theorem, and it is not
an input to Phase 6 certificates. Phase 7 records substantial overlap with its
paradoxical-sequence and continued-fraction setting. Phase 8 isolates Lemma
B.1 as EXT05 and applies it only with exponent `q>=30`; therefore the C02 proof
does not use the paper's separate finite check for `13<=q<=18`.
Phase 9 independently enumerates only shortcut lengths through 21 and does not
reprove Theorem 1.3, its `2.8*10^19` bound, or its conditional equivalence.

### Winkler (2017; revised 2026)

**Status:** `EXTERNAL_THEOREM`; finite coefficient-stopping structure, not an
active proof dependency

Mike Winkler, “Deterministic Structures in the Stopping Time Dynamics of the
3x+1 Problem,” arXiv:1709.03385v8 (2017; revised 2026).
[arXiv:1709.03385](https://arxiv.org/abs/1709.03385).

**Result relevant here.** The current manuscript characterizes admissible odd
position vectors at each finite order as a directed rooted tree, gives a
Pascal-type exact recursion, and reconstructs the associated residue classes
and periodic finite-order coverage.

**Repository role.** This is direct prior overlap for Phase 9's small-layer
first-crossing enumeration and for any future recursive state design. The
paper explicitly limits the conclusions to finite coefficient-stopping
structures; it does not prove that every start has finite coefficient stopping
time or identify coefficient stopping with classical stopping time. Phase 9's
independent q<=21 digests do not reproduce the full external manuscript.

### Winkler (2015; revised 2021)

**Status:** `EXTERNAL_EVIDENCE`; conjectural counting formula, not a proof
dependency

Mike Winkler, “New results on the stopping time behaviour of the Collatz 3x +
1 function,” arXiv:1504.00212v4 (2015; revised 2021).
[arXiv:1504.00212](https://arxiv.org/abs/1504.00212).

**Result relevant here.** The manuscript studies the finite-order counts now
listed as OEIS A100982 and proposes an iterative formula for them.

**Repository role.** It is historical overlap for the Phase 7/9 layer counts,
not an axiom: the current artifacts derive every audited count and row digest
internally. The formula is recorded as conjectural in the source abstract and
is not promoted here.

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

## Computational verification bound

### Barina convergence-verification project

**Status:** `EXTERNAL_EVIDENCE`; active numerical input X02

David Barina, [“Convergence verification of the Collatz
problem”](https://pcbarina.fit.vut.cz/), live project status and public source
code. The related published algorithmic reports include “Improved verification
limit for the convergence of the Collatz conjecture,” *The Journal of
Supercomputing* **81** (2025), article 810,
[DOI 10.1007/s11227-025-07337-0](https://doi.org/10.1007/s11227-025-07337-0).

**Result relevant here.** On 2026-08-27 the live primary status page stated
that every positive start below `2075*2^60` had been verified to converge and
that the next block was still in progress.

**Repository role.** X02 uses only the completed lower boundary
`2075*2^60`. Phase 7 onward checks exact consequences after substituting it,
but this repository does not reproduce the distributed global computation or
certify its work-unit provenance. Progress toward `2076*2^60` is not imported
until the completed boundary changes and is re-audited. No finite verification
bound proves Collatz.

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

1. an independent specialist review of the López--Stoll (2021) proof itself
   before EXT08 is ever used inside a claimed full Collatz proof; Phase 20 has
   already audited the map, rational domain, theorem/proof location, and
   `liminf` quantifier;
2. the derivation, exponent rounding, and effective constants in converting
   Wu–Wang to the contextual `H_q = O(q^5.117)` statement;
3. the complete proof chain from Ellison's Theorem 3 to Rozier--Terracol Lemma
   B.1 if EXT05 ever becomes part of a claimed full Collatz proof.
