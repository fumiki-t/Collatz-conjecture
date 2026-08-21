"""Exact first-return model on S = {n: n == 2 (mod 9)}."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd


SECTION_RESIDUE = 2
SECTION_MODULUS = 9
KAPPA = {0: 1, 2: 5, 4: 21}


def ceil_div(a: int, b: int) -> int:
    if b <= 0:
        raise ValueError("divisor must be positive")
    return -((-a) // b)


def shortcut_step(n: int) -> int:
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def first_return(n: int, *, max_steps: int = 100_000) -> tuple[int, str]:
    if n % SECTION_MODULUS != SECTION_RESIDUE:
        raise ValueError("start is outside the 2 mod 9 section")
    value = n
    bits: list[str] = []
    for _ in range(max_steps):
        bits.append(str(value % 2))
        value = shortcut_step(value)
        if value % SECTION_MODULUS == SECTION_RESIDUE:
            return value, "".join(bits)
    raise RuntimeError("first return was not found within the explicit step bound")


@dataclass(frozen=True, slots=True)
class ReturnTemplate:
    name: str
    word: str
    source_base: int
    source_step: int
    output_base: int
    output_step: int
    kind: str
    c: int | None = None
    a: int | None = None
    b: int | None = None
    v_residue: int | None = None

    def values(self, parameter: int) -> tuple[int, int]:
        if parameter < 0:
            raise ValueError("template parameter must be non-negative")
        return (
            self.source_base + self.source_step * parameter,
            self.output_base + self.output_step * parameter,
        )

    def compact(self) -> dict[str, object]:
        return {
            "name": self.name,
            "word": self.word,
            "source": [self.source_base, self.source_step],
            "output": [self.output_base, self.output_step],
            "kind": self.kind,
            "c": self.c,
            "a": self.a,
            "b": self.b,
            "v_residue_mod_12": self.v_residue,
        }


def parameter_residue(c: int, a: int, b: int) -> int:
    if c not in (0, 2, 4) or b not in (0, 1):
        raise ValueError("invalid parametric return branch")
    if (c in (0, 2) and a < 1) or (c == 4 and a < 0):
        raise ValueError("invalid run length")
    if c == 0:
        wanted_mod3 = 1 if a % 2 == 0 else 2
    elif c == 2:
        wanted_mod3 = 2 if a % 2 == 0 else 1
    else:
        wanted_mod3 = 0
    wanted_mod4 = 1 if b == 0 else 3
    for residue in range(1, 12, 2):
        if (
            residue % 3 == wanted_mod3
            and (pow(3, a + 1, 4) * residue) % 4 == wanted_mod4
        ):
            return residue
    raise AssertionError("CRT residue was not found")


def parametric_template(c: int, a: int, b: int) -> ReturnTemplate:
    residue = parameter_residue(c, a, b)
    scale = 1 << c
    source_base = scale * (3 * (1 << a) * residue - 1)
    source_step = scale * 3 * (1 << a) * 12
    numerator = pow(3, a + b + 1) * residue - 1
    if numerator % 4:
        raise AssertionError("return numerator is not divisible by four")
    output_base = numerator // 4
    output_step = pow(3, a + b + 2)
    return ReturnTemplate(
        f"c{c}-a{a}-b{b}",
        "0" * c + "1" * a + "0" + str(b),
        source_base,
        source_step,
        output_base,
        output_step,
        "PARAMETRIC",
        c,
        a,
        b,
        residue,
    )


def return_templates(max_a: int) -> list[ReturnTemplate]:
    if max_a < 1:
        raise ValueError("max_a must be at least one")
    templates = [
        ReturnTemplate("special-01", "01", 2, 36, 2, 27, "SPECIAL"),
        ReturnTemplate("special-0001", "0001", 56, 144, 11, 27, "SPECIAL"),
    ]
    for c in (0, 2, 4):
        first_a = 0 if c == 4 else 1
        for a in range(first_a, max_a + 1):
            for b in (0, 1):
                templates.append(parametric_template(c, a, b))
    return templates


def formula_from_word(n: int, word: str) -> dict[str, object]:
    if word == "01":
        if (n - 2) % 36:
            raise ValueError("invalid special 01 source")
        v = (n - 2) // 36
        return {"kind": "SPECIAL", "word": word, "v": v, "return": 27 * v + 2}
    if word == "0001":
        if (n - 56) % 144:
            raise ValueError("invalid special 0001 source")
        v = (n - 56) // 144
        return {"kind": "SPECIAL", "word": word, "v": v, "return": 27 * v + 11}

    if word.startswith("1"):
        c = 0
    elif word.startswith("001"):
        c = 2
    elif word.startswith("0000"):
        c = 4
    else:
        raise ValueError(f"word is not in the first-return code: {word}")
    cursor = c
    a = 0
    while cursor < len(word) and word[cursor] == "1":
        a += 1
        cursor += 1
    if cursor + 2 != len(word) or word[cursor] != "0" or word[-1] not in "01":
        raise ValueError("malformed parametric return word")
    b = int(word[-1])
    if (c in (0, 2) and a < 1) or (c == 4 and a < 0):
        raise ValueError("invalid parametric run length")
    scaled = n // (1 << c)
    if n % (1 << c) or (scaled + 1) % (3 * (1 << a)):
        raise ValueError("source does not have the claimed parameterization")
    v = (scaled + 1) // (3 * (1 << a))
    if v <= 0 or v % 2 == 0:
        raise ValueError("v is not a positive odd integer")
    residue = parameter_residue(c, a, b)
    if v % 12 != residue:
        raise ValueError("v violates an exact mod-3/mod-4 domain condition")
    numerator = pow(3, a + b + 1) * v - 1
    if numerator % 4:
        raise ValueError("return formula is not integral")
    return {
        "kind": "PARAMETRIC",
        "word": word,
        "c": c,
        "a": a,
        "b": b,
        "v": v,
        "v_residue_mod_12": residue,
        "return": numerator // 4,
    }


def z_from_n(n: int) -> int:
    numerator = 4 * n + 1
    if numerator % 3:
        raise ValueError("n is outside the z-coordinate domain")
    return numerator // 3


def n_from_z(z: int) -> int:
    numerator = 3 * z - 1
    if numerator % 4:
        raise ValueError("z is outside the n-coordinate domain")
    return numerator // 4


def parametric_z_identity(c: int, a: int, b: int, v: int) -> tuple[int, int]:
    if v % 12 != parameter_residue(c, a, b):
        raise ValueError("v violates the branch domain")
    z = (1 << (a + c + 2)) * v - KAPPA[c]
    z_next = pow(3, a + b) * v
    return z, z_next


@dataclass(frozen=True, slots=True)
class ReturnFamily:
    source_base: int
    source_step: int
    endpoint_base: int
    endpoint_step: int
    history: tuple[str, ...]
    words: tuple[str, ...]
    parent_id: int | None = None
    composition: tuple[int, int, int, int] | None = None

    @property
    def depth(self) -> int:
        return len(self.history)

    def values(self, parameter: int) -> tuple[int, int]:
        if parameter < 0:
            raise ValueError("family parameter must be non-negative")
        return (
            self.source_base + self.source_step * parameter,
            self.endpoint_base + self.endpoint_step * parameter,
        )

    def compact(self) -> dict[str, object]:
        return {
            "source": [self.source_base, self.source_step],
            "endpoint": [self.endpoint_base, self.endpoint_step],
            "history": list(self.history),
            "words": list(self.words),
            "parent_id": self.parent_id,
            "composition": list(self.composition) if self.composition else None,
        }


def root_family(template: ReturnTemplate) -> ReturnFamily:
    return ReturnFamily(
        template.source_base,
        template.source_step,
        template.output_base,
        template.output_step,
        (template.name,),
        (template.word,),
    )


def compose_with_template(
    family: ReturnFamily,
    template: ReturnTemplate,
    parent_id: int,
) -> ReturnFamily | None:
    a = family.endpoint_step
    modulus = template.source_step
    difference = template.source_base - family.endpoint_base
    common = gcd(a, modulus)
    if difference % common:
        return None
    period = modulus // common
    if period == 1:
        parameter_base = 0
    else:
        parameter_base = (
            (difference // common) * pow(a // common, -1, period)
        ) % period
    template_parameter_base = (
        family.endpoint_base
        + a * parameter_base
        - template.source_base
    ) // modulus
    template_parameter_step = a // common
    shift = max(0, ceil_div(-template_parameter_base, template_parameter_step))
    parameter_base += period * shift
    template_parameter_base += template_parameter_step * shift
    if template_parameter_base < 0:
        raise AssertionError("composition positivity adjustment failed")
    return ReturnFamily(
        family.source_base + family.source_step * parameter_base,
        family.source_step * period,
        template.output_base + template.output_step * template_parameter_base,
        template.output_step * template_parameter_step,
        family.history + (template.name,),
        family.words + (template.word,),
        parent_id,
        (
            parameter_base,
            period,
            template_parameter_base,
            template_parameter_step,
        ),
    )


def descent_high(family: ReturnFamily) -> int | None:
    if family.endpoint_step >= family.source_step:
        return None
    return (family.endpoint_base - family.source_base) // (
        family.source_step - family.endpoint_step
    )


def is_uniform_smaller(family: ReturnFamily) -> bool:
    slope_difference = family.endpoint_step - family.source_step
    return slope_difference <= 0 and family.endpoint_base < family.source_base


def recurrence_identity(c: int, a: int, b: int, v: int) -> tuple[int, int]:
    kappa = KAPPA[c]
    bracket = (pow(3, a + b) - (1 << (a + c + 2))) * v + kappa
    if 3 * bracket % 4:
        raise ValueError("recurrence difference is not integral")
    n = (1 << c) * (3 * (1 << a) * v - 1)
    returned = (pow(3, a + b + 1) * v - 1) // 4
    return returned - n, 3 * bracket // 4


def affine_fixed_point(multiplier: int, constant: int, denominator: int) -> Fraction | None:
    delta = denominator - multiplier
    return None if delta == 0 else Fraction(constant, delta)
