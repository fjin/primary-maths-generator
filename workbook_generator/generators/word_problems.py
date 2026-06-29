from __future__ import annotations

import random

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question
from workbook_generator.question_bank import QuestionBank


class WordProblemGenerator(BaseGenerator):
    topic = "word_problems"

    def __init__(self, question_bank: QuestionBank | None = None) -> None:
        self.question_bank = question_bank or QuestionBank()

    def generate_one(self, rng: random.Random, difficulty: int) -> Question:
        bank_question = self.question_bank.generate_one(self.topic, difficulty, rng)
        if bank_question:
            return bank_question

        boxes = rng.randint(3, 12)
        per_box = rng.randint(8, 24)
        used = rng.randint(5, boxes * per_box // 2)
        answer = boxes * per_box - used
        prompt = (
            f"There are {boxes} boxes with {per_box} pencils in each box. "
            f"After {used} pencils are used, how many are left?"
        )
        return Question(
            prompt=prompt,
            answer=str(answer),
            topic=self.topic,
            subtopic="multi_step",
            difficulty=difficulty,
            tags=("word_problem",),
        )
