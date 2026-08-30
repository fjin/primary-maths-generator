from __future__ import annotations

import random

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question
from workbook_generator.question_bank import QuestionBank


class NumberPatternGenerator(BaseGenerator):
    topic = "number_patterns"

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
        raise ValueError("No number-pattern questions found in the question bank.")
