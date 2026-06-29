from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from fractions import Fraction
from typing import Any


@dataclass(frozen=True)
class Question:
    prompt: str
    answer: str
    topic: str
    subtopic: str
    difficulty: int
    tags: tuple[str, ...] = ()
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Worksheet:
    title: str
    slug: str
    questions: list[Question]
    seed: int
    difficulty: str
    created_on: date = field(default_factory=date.today)


def latex_fraction(value: Fraction, mixed: bool = True) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    if mixed and abs(value.numerator) > value.denominator:
        whole = value.numerator // value.denominator
        remainder = abs(value.numerator) % value.denominator
        return rf"{whole}\dfrac{{{remainder}}}{{{value.denominator}}}"
    return rf"\dfrac{{{value.numerator}}}{{{value.denominator}}}"


def dollars(cents: int) -> str:
    return rf"\${cents / 100:.2f}"
