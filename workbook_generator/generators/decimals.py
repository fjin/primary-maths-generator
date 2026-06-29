from __future__ import annotations

import random
from decimal import Decimal

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question


class DecimalGenerator(BaseGenerator):
    topic = "decimals"

    def generate_one(self, rng: random.Random, difficulty: int) -> Question:
        scale = 10 if difficulty <= 3 else 100
        a = Decimal(rng.randint(10, 900)) / scale
        b = Decimal(rng.randint(10, 500)) / scale
        operation = rng.choice(["+", "-"])
        if operation == "-" and b > a:
            a, b = b, a
        answer = a + b if operation == "+" else a - b
        return Question(
            prompt=rf"${a} {operation} {b} =$",
            answer=rf"${self._format(answer)}$",
            topic=self.topic,
            subtopic="operations",
            difficulty=difficulty,
            tags=("decimal",),
        )

    @staticmethod
    def _format(value: Decimal) -> str:
        formatted = format(value.normalize(), "f")
        return formatted.rstrip("0").rstrip(".") if "." in formatted else formatted
