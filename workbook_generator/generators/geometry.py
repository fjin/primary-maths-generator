from __future__ import annotations

import random

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question


class GeometryGenerator(BaseGenerator):
    topic = "geometry"

    def generate_one(self, rng: random.Random, difficulty: int) -> Question:
        shape = rng.choice(["rectangle", "triangle"])
        if shape == "rectangle":
            length = rng.randint(4, 20)
            width = rng.randint(3, 15)
            answer = length * width
            prompt = rf"A rectangle is ${length}$ cm by ${width}$ cm. Find its area."
        else:
            base = rng.randint(4, 20)
            height = rng.choice([4, 6, 8, 10, 12, 14])
            answer = base * height // 2
            prompt = rf"A triangle has base ${base}$ cm and height ${height}$ cm. Find its area."
        return Question(
            prompt=prompt,
            answer=rf"${answer}\text{{ cm}}^2$",
            topic=self.topic,
            subtopic="area",
            difficulty=difficulty,
            tags=("geometry", "area"),
        )

