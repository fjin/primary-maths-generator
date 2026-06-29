from __future__ import annotations

import random

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question, dollars


class MoneyGenerator(BaseGenerator):
    topic = "money"

    def generate_one(self, rng: random.Random, difficulty: int) -> Question:
        price = rng.randint(150, 2500)
        paid = ((price // 500) + rng.randint(1, 4)) * 500
        change = paid - price
        return Question(
            prompt=f"An item costs {dollars(price)}. If you pay {dollars(paid)}, how much change do you receive?",
            answer=dollars(change),
            topic=self.topic,
            subtopic="change",
            difficulty=difficulty,
            tags=("money",),
        )

