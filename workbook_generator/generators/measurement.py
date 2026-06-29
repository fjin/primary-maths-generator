from __future__ import annotations

import random

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question


class MeasurementGenerator(BaseGenerator):
    topic = "measurement"

    def generate_one(self, rng: random.Random, difficulty: int) -> Question:
        metres = rng.randint(1, 12)
        centimetres = rng.choice([5, 10, 15, 20, 25, 50, 75])
        total = metres * 100 + centimetres
        return Question(
            prompt=rf"Convert ${metres}$ m ${centimetres}$ cm to centimetres.",
            answer=rf"${total}$ cm",
            topic=self.topic,
            subtopic="unit_conversion",
            difficulty=difficulty,
            tags=("measurement", "conversion"),
        )

