from __future__ import annotations

import random

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question, dollars
from workbook_generator.question_bank import QuestionBank


class MoneyGenerator(BaseGenerator):
    topic = "money"

    def __init__(self, question_bank: QuestionBank | None = None) -> None:
        self.question_bank = question_bank or QuestionBank()

    def generate_one(
        self,
        rng: random.Random,
        difficulty: int,
        subtopics: list[str] | None = None,
    ) -> Question:
        bank_question = self.question_bank.generate_one(
            self.topic,
            difficulty,
            rng,
            subtopics=subtopics,
        )
        if bank_question:
            return bank_question

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
