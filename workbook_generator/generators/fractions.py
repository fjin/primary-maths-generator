from __future__ import annotations

import random
from fractions import Fraction

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question, latex_fraction


class FractionGenerator(BaseGenerator):
    topic = "fractions"

    def generate_one(self, rng: random.Random, difficulty: int) -> Question:
        denominators = [2, 3, 4, 5, 6, 8, 10, 12]
        denominator_a = rng.choice(denominators[: 4 + difficulty])
        denominator_b = rng.choice(denominators[: 4 + difficulty])
        a = Fraction(rng.randint(1, denominator_a - 1), denominator_a)
        b = Fraction(rng.randint(1, denominator_b - 1), denominator_b)
        operation = rng.choice(["+", "-"] if difficulty < 4 else ["+", "-", r"\times"])

        if operation == "+":
            answer = a + b
        elif operation == "-":
            if b > a:
                a, b = b, a
            answer = a - b
        else:
            answer = a * b

        prompt = rf"${latex_fraction(a, mixed=False)} {operation} {latex_fraction(b, mixed=False)} =$"
        return Question(
            prompt=prompt,
            answer=rf"${latex_fraction(answer)}$",
            topic=self.topic,
            subtopic="operations",
            difficulty=difficulty,
            tags=("fraction", "arithmetic"),
        )

