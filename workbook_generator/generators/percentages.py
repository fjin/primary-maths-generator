from __future__ import annotations

import random

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question


class PercentageGenerator(BaseGenerator):
    topic = "percentages"

    def generate_one(self, rng: random.Random, difficulty: int) -> Question:
        percent = rng.choice([5, 10, 15, 20, 25, 30, 40, 50, 75])
        base = rng.choice([40, 60, 80, 100, 120, 160, 200, 240, 320])
        answer = base * percent // 100
        return Question(
            prompt=rf"What is ${percent}\%$ of ${base}$?",
            answer=rf"${answer}$",
            topic=self.topic,
            subtopic="percent_of_amount",
            difficulty=difficulty,
            tags=("percentage",),
        )

