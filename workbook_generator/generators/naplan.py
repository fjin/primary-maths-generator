from __future__ import annotations

import random

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question


class NaplanGenerator(BaseGenerator):
    topic = "naplan"

    def generate_one(self, rng: random.Random, difficulty: int) -> Question:
        number = rng.randint(2000, 99999)
        place = rng.choice([10, 100, 1000])
        rounded = ((number + place // 2) // place) * place
        return Question(
            prompt=rf"Round ${number}$ to the nearest ${place}$.",
            answer=rf"${rounded}$",
            topic=self.topic,
            subtopic="number",
            difficulty=max(difficulty, 4),
            tags=("naplan", "rounding"),
        )
